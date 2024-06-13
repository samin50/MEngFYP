"""
Pygame Frontend for the Pi4
Displays on the 7 inch Dfrobot LCD
"""
import os
import colorsys
import psutil
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIHorizontalSlider, UILabel, UIButton
from src.common.constants import LCD_RESOLUTION, CAMERA_DISPLAY_SIZE, WIDGET_PADDING, STAT_REFRESH_INTERVAL, BG_COLOUR, THEMEJSON, SHOW_CURSOR, TRAINING_MODE_CAMERA_SIZE, COLOURS
from src.common.helper_functions import start_ui, wifi_restart
from src.common.custom_pygame_widgets import CustomToggleButton
from src.pi4.vision_handler import Vision_Handler

class LCD_UI:
    def __init__(self, clock:pygame.time.Clock, visionHandler:Vision_Handler, callbacks:dict={}, trainingMode:bool=False, resizeable:bool=False) -> None:
        self.running = True
        self.trainingMode = trainingMode
        # Setup UI
        self.display = pygame.display.set_mode(LCD_RESOLUTION, resizeable and (pygame.RESIZABLE | pygame.SCALED))
        pygame.display.set_caption("Component Sorter")
        self.clock = clock
        self.resolution = TRAINING_MODE_CAMERA_SIZE if self.trainingMode else CAMERA_DISPLAY_SIZE
        self.componentResolution = self.resolution[0]//3, self.resolution[1]
        self.cameraSurface = pygame.Surface(self.resolution)
        self.componentSurface = pygame.Surface(self.componentResolution)
        self.visionHandler = visionHandler.init(self.cameraSurface, self.componentSurface, trainingMode=self.trainingMode)
        self.manager = pygame_gui.UIManager(LCD_RESOLUTION, theme_path=THEMEJSON, enable_live_theme_updates=False)
        self.UIElements = dict()
        # Setup Event
        self.statUpdateEvent = pygame.USEREVENT + 101
        pygame.time.set_timer(self.statUpdateEvent, STAT_REFRESH_INTERVAL)
        self.cpuColour = ""
        self.ramColour = ""
        self.latencyColour = ""
        self.confidenceColour = ""
        # Training mode setup
        self.init_ui_widgets()
        # Cursor
        if SHOW_CURSOR:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        # Callback functions
        self.stripResetCallback = callbacks.get("strip_reset_callback", lambda: None)
        self.colourCallback = callbacks.get("colour_callback", lambda _: None)
        self.conveyorSpeedCallback = callbacks.get("conveyor_speed_callback", lambda _: None)
        # Callbacks
        self.visionHandler.set_lcd_callbacks({
            "update_inference_time" : self.set_latency,
            "update_confidence" : self.set_confidence,
            "update_class" : self.set_class,
        })

    def set_latency(self, latency:int) -> None:
        """
        Set the latency
        """
        latency = latency*1000
        self.UIElements["inference_latency"].set_text(f"{latency:.2f}ms")
        if latency > 1000:
            latencyColour = COLOURS["red"]
        elif latency > 500:
            latencyColour = COLOURS["yellow"]
        else:
            latencyColour = COLOURS["green"]
        if self.latencyColour != latencyColour:
            self.UIElements["inference_latency"].text_colour = pygame.Color(latencyColour)
            self.UIElements["inference_latency"].rebuild()
            self.latencyColour = latencyColour

    def set_confidence(self, confidence:float) -> None:
        """
        Set the confidence
        """
        if confidence > 80:
            confidenceColour = COLOURS["green"]
        elif confidence > 60:
            confidenceColour = COLOURS["yellow"]
        else:
            confidenceColour = COLOURS["red"]
        self.UIElements["confidence_label"].set_text(f"{int(confidence)}%")
        if self.confidenceColour != confidenceColour:
            self.UIElements["confidence_label"].text_colour = pygame.Color(confidenceColour)
            self.UIElements["confidence_label"].rebuild()
            self.confidenceColour = confidenceColour

    def set_class(self, cls:str) -> None:
        """
        Set the class
        """
        self.UIElements["class_label"].set_text(cls)

    def is_running(self) -> bool:
        """
        Check if the UI is running
        """
        return self.running

    def init_ui_widgets(self) -> None:
        """
        Draw the UI widgets - code is messy because of absolute positioning and training mode
        """
        # Widget Parameters
        sliderHeight = 30
        offset = 2
        cornerOffset = (WIDGET_PADDING, WIDGET_PADDING)
        buttonHeight = 60
        # Training mode
        if self.trainingMode:
            cornerOffset = (740, 0)
            global CAMERA_DISPLAY_SIZE # pylint:disable=global-statement
            CAMERA_DISPLAY_SIZE = (240, 360) # pylint:disable=redefined-outer-name, invalid-name
            widgetWidth = 50
        widgetWidth = (CAMERA_DISPLAY_SIZE[0]-WIDGET_PADDING)/2
        textWidth = 80
        offsetIncrement = sliderHeight + WIDGET_PADDING
        yOffset = 2*WIDGET_PADDING
        ## LEFT SIDE
        if not self.trainingMode:
            _ = UILabel(
                relative_rect=pygame.Rect((cornerOffset[0]+offset, CAMERA_DISPLAY_SIZE[1]+yOffset), (widgetWidth, sliderHeight)),
                text="System Speed:",
                manager=self.manager
            )
            self.UIElements["system_speed_label"] = UILabel(
                relative_rect=pygame.Rect((cornerOffset[0]+widgetWidth-textWidth, CAMERA_DISPLAY_SIZE[1]+yOffset), (textWidth, sliderHeight)),
                text="0",
                manager=self.manager,
                object_id=ObjectID(class_id="label", object_id="#right_label")
            )
            self.UIElements["system_speed"] = UIHorizontalSlider(
                relative_rect=pygame.Rect((cornerOffset[0]+widgetWidth+WIDGET_PADDING, CAMERA_DISPLAY_SIZE[1]+yOffset), (widgetWidth+offset, sliderHeight)),
                value_range=(-5, 5),
                start_value=0,
                manager=self.manager
            )
        xModifier = 0
        if self.trainingMode:
            xModifier = widgetWidth
            yOffset -= 2*buttonHeight
        # CPU Usage
        yOffset += offsetIncrement
        _ = UILabel(
            relative_rect=pygame.Rect((cornerOffset[0]+offset, CAMERA_DISPLAY_SIZE[1]+yOffset), (widgetWidth, sliderHeight)),
            text="CPU Usage: ",
            manager=self.manager
        )
        self.UIElements["cpu_usage_label"] = UILabel(
            relative_rect=pygame.Rect((cornerOffset[0]+widgetWidth-textWidth+xModifier, CAMERA_DISPLAY_SIZE[1]+yOffset), (textWidth, sliderHeight)),
            text="-%",
            manager=self.manager,
            object_id=ObjectID(class_id="label", object_id="#right_label")
        )
        yOffset += offsetIncrement if self.trainingMode else 0
        # RAM Usage
        _ = UILabel(
            relative_rect=pygame.Rect((cornerOffset[0]+widgetWidth+WIDGET_PADDING-xModifier, CAMERA_DISPLAY_SIZE[1]+yOffset), (widgetWidth, sliderHeight)),
            text="RAM Usage: ",
            manager=self.manager,
        )
        self.UIElements["ram_usage_label"] = UILabel(
            relative_rect=pygame.Rect((cornerOffset[0]+2*widgetWidth-textWidth+WIDGET_PADDING, CAMERA_DISPLAY_SIZE[1]+yOffset), (textWidth, sliderHeight)),
            text="-%",
            manager=self.manager,
            object_id=ObjectID(class_id="label", object_id="#right_label")
        )
        # Heatmap toggle button
        yOffset += offsetIncrement
        self.UIElements["wifi_status"] = UILabel(
            relative_rect=pygame.Rect((cornerOffset[0], CAMERA_DISPLAY_SIZE[1]+yOffset), (widgetWidth, buttonHeight)),
            text="WiFi: Not Connected",
            manager=self.manager,
        )
        # Wifi Button
        self.UIElements["wifi_button"] = UIButton(
            relative_rect=pygame.Rect((cornerOffset[0]+widgetWidth+WIDGET_PADDING, CAMERA_DISPLAY_SIZE[1]+yOffset), (widgetWidth+offset, buttonHeight)),
            text="Wifi Restart",
            manager=self.manager
        )
        # Exit Button
        yOffset += buttonHeight + WIDGET_PADDING
        self.UIElements["exit_button"] = UIButton(
            relative_rect=pygame.Rect((cornerOffset[0], LCD_RESOLUTION[1]-buttonHeight-WIDGET_PADDING), (widgetWidth*2+WIDGET_PADDING+offset, buttonHeight)),
            text="Exit",
            manager=self.manager
        )
        ## RIGHT SIDE
        if self.trainingMode:
            xOffset = cornerOffset[0]
            yOffset = WIDGET_PADDING
        else:
            xOffset = CAMERA_DISPLAY_SIZE[0] + 2*WIDGET_PADDING
            yOffset = WIDGET_PADDING-3
        widgetWidth = (LCD_RESOLUTION[0] - CAMERA_DISPLAY_SIZE[0] - 4*WIDGET_PADDING - self.componentResolution[0])//2
        # Classification Label
        if not self.trainingMode:
            _ = UILabel(
                relative_rect=pygame.Rect((xOffset+offset, yOffset), (widgetWidth, sliderHeight)),
                text="Class:",
                manager=self.manager
            )
            self.UIElements["class_label"] = UILabel(
                relative_rect=pygame.Rect((xOffset+widgetWidth, yOffset), (widgetWidth, sliderHeight)),
                text="None",
                manager=self.manager,
                object_id=ObjectID(class_id="label", object_id="#right_label")
            )
            yOffset += offsetIncrement
            # Confidence Label
            _ = UILabel(
                relative_rect=pygame.Rect((xOffset+offset, yOffset), (widgetWidth, sliderHeight)),
                text="Conf:",
                manager=self.manager
            )
            self.UIElements["confidence_label"] = UILabel(
                relative_rect=pygame.Rect((xOffset+widgetWidth-textWidth, yOffset), (textWidth, sliderHeight)),
                text="-%",
                manager=self.manager,
                object_id=ObjectID(class_id="label", object_id="#right_label")
            )
            # Value Label
            _ = UILabel(
                relative_rect=pygame.Rect((xOffset+offset+widgetWidth+WIDGET_PADDING, yOffset), (CAMERA_DISPLAY_SIZE[0]-widgetWidth, sliderHeight)),
                text="Value:",
                manager=self.manager
            )
            self.UIElements["value_label"] = UILabel(
                relative_rect=pygame.Rect((xOffset+widgetWidth, yOffset), (widgetWidth, sliderHeight)),
                text="N/A",
                manager=self.manager,
                object_id=ObjectID(class_id="label", object_id="#right_label")
            )
            yOffset += offsetIncrement
            # Offload inference button
            self.UIElements["offload_inference"] = CustomToggleButton(
                relative_rect=pygame.Rect((xOffset, yOffset), ((widgetWidth*2)+offset, buttonHeight)),
                text="Offload Inference?",
                manager=self.manager
            )
            # Connection status
            yOffset += buttonHeight + WIDGET_PADDING
            _ = UILabel(
                relative_rect=pygame.Rect((xOffset, yOffset), (widgetWidth*2, sliderHeight)),
                text="Compute:",
                manager=self.manager
            )
            self.UIElements["compute_status"] = UILabel(
                relative_rect=pygame.Rect((xOffset, yOffset), (widgetWidth*2, sliderHeight)),
                text="Local",
                manager=self.manager,
                object_id=ObjectID(class_id="label", object_id="#right_label")
            )
            # Inference button
            yOffset += sliderHeight + WIDGET_PADDING
            self.UIElements["const_inference"] = CustomToggleButton(
                relative_rect=pygame.Rect((xOffset, yOffset), (widgetWidth*2, buttonHeight)),
                text="Const. Inference?",
                manager=self.manager
            )
            # Inferenece latency
            yOffset += buttonHeight + WIDGET_PADDING
            _ = UILabel(
                relative_rect=pygame.Rect((xOffset, yOffset), (widgetWidth*2-textWidth, sliderHeight)),
                text="Latency:",
                manager=self.manager
            )
            self.UIElements["inference_latency"] = UILabel(
                relative_rect=pygame.Rect((xOffset+widgetWidth*2-textWidth*2, yOffset), (2*textWidth, sliderHeight)),
                text="-ms",
                manager=self.manager,
                object_id=ObjectID(class_id="label", object_id="#right_label")
            )
            # Inference once button
            yOffset += sliderHeight + WIDGET_PADDING + 5
            self.UIElements["inference_once"] = UIButton(
                relative_rect=pygame.Rect((xOffset, yOffset), (widgetWidth*2, buttonHeight)),
                text="Inference Once",
                manager=self.manager
            )
            # After component display
            # Status
            yOffset = CAMERA_DISPLAY_SIZE[1]+ 2*WIDGET_PADDING
            widgetWidth = (LCD_RESOLUTION[0] - CAMERA_DISPLAY_SIZE[0] - 4*WIDGET_PADDING)//2
            _ = UILabel(
                relative_rect=pygame.Rect((xOffset, yOffset), (widgetWidth, buttonHeight)),
                text="Status:",
                manager=self.manager,
                object_id=ObjectID(class_id="label", object_id="#top_label")
            )
            self.UIElements["status_label"] = UILabel(
                relative_rect=pygame.Rect((xOffset, yOffset), (LCD_RESOLUTION[0] - CAMERA_DISPLAY_SIZE[0] - 4*WIDGET_PADDING-self.componentResolution[0], buttonHeight)),
                text="Idle",
                manager=self.manager,
                object_id=ObjectID(class_id="label", object_id="#topright_label")
            )
            self.UIElements["status_label"].text_colour = pygame.Color(COLOURS["yellow"])
            self.UIElements["status_label"].rebuild()
            self.UIElements["status_description"] = UILabel(
                relative_rect=pygame.Rect((xOffset, yOffset+WIDGET_PADDING+3), (LCD_RESOLUTION[0] - CAMERA_DISPLAY_SIZE[0] - 4*WIDGET_PADDING-self.componentResolution[0], buttonHeight)),
                text="System Inactive",
                manager=self.manager,
                object_id=ObjectID(class_id="label", object_id="#center_label")
            )
            # Enable button
            self.UIElements["enable_button"] = CustomToggleButton(
                relative_rect=pygame.Rect((LCD_RESOLUTION[0]-WIDGET_PADDING-self.componentResolution[0]-offset, yOffset), (self.componentResolution[0]+2*offset, buttonHeight+2*offset)),
                text="Enabled?",
                manager=self.manager
            )
        # Colour strip
        yOffset += buttonHeight + WIDGET_PADDING*2
        offsetIncrement = sliderHeight
        sliderModifier = 0
        sliderModifierHeight = 0
        sliderWidth = (LCD_RESOLUTION[0] - CAMERA_DISPLAY_SIZE[0] - 5*WIDGET_PADDING)//3 + 1
        if self.trainingMode:
            yOffset = 2*WIDGET_PADDING
            sliderModifier = sliderWidth
            sliderModifierHeight = buttonHeight + WIDGET_PADDING
        self.UIElements["hue_slider"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((xOffset, yOffset), (sliderWidth, sliderHeight)),
            value_range=(0, 180),
            start_value=90,
            click_increment=10,
            manager=self.manager
        )
        self.UIElements["saturation_slider"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((xOffset+sliderWidth+WIDGET_PADDING-sliderModifier, yOffset+sliderModifierHeight), (sliderWidth, sliderHeight)),
            value_range=(0, 100),
            start_value=50,
            click_increment=10,
            manager=self.manager
        )
        self.UIElements["value_slider"] = UIHorizontalSlider(
            relative_rect=pygame.Rect((xOffset+2*sliderWidth+2*WIDGET_PADDING-(2*sliderModifier), yOffset+2*sliderModifierHeight), (sliderWidth, sliderHeight)),
            value_range=(0, 100),
            start_value=50,
            click_increment=10,
            manager=self.manager
        )
        # Labels
        yOffset += offsetIncrement + WIDGET_PADDING // 2
        self.UIElements["hue_slider_label"] = UILabel(
            relative_rect=pygame.Rect((xOffset, yOffset), (sliderWidth, sliderHeight)),
            text="Hue: 90",
            manager=self.manager,
            object_id=ObjectID(class_id="label", object_id="#center_label")
        )
        self.UIElements["saturation_slider_label"] = UILabel(
            relative_rect=pygame.Rect((xOffset+sliderWidth+WIDGET_PADDING-sliderModifier, yOffset+sliderModifierHeight), (sliderWidth, sliderHeight)),
            text="Sat: 50",
            manager=self.manager,
            object_id=ObjectID(class_id="label", object_id="#center_label")
        )
        self.UIElements["value_slider_label"] = UILabel(
            relative_rect=pygame.Rect((xOffset+2*sliderWidth+2*WIDGET_PADDING-(2*sliderModifier), yOffset+2*sliderModifierHeight), (sliderWidth, sliderHeight)),
            text="Val: 50",
            manager=self.manager,
            object_id=ObjectID(class_id="label", object_id="#center_label")
        )
        self.UIElements["strip_reset_button"] = UIButton(
            relative_rect=pygame.Rect((xOffset, LCD_RESOLUTION[1]-buttonHeight-WIDGET_PADDING-sliderModifierHeight), (widgetWidth*2+WIDGET_PADDING-sliderModifier, buttonHeight)),
            text="Reset Strip",
            manager=self.manager
        )
        if self.trainingMode:
            self.UIElements["take_photo_button"] = UIButton(
                relative_rect=pygame.Rect((xOffset, yOffset+offsetIncrement*6), (CAMERA_DISPLAY_SIZE[0]+WIDGET_PADDING, buttonHeight)),
                text="Take Photo",
                manager=self.manager
            )

    def handle_events(self, event:pygame.event) -> None:
        """
        Handle events from the UI
        """
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.UIElements.get("system_speed", None):
                self.UIElements["conveyor_speed_label"].set_text(f"Conveyor Speed: {(event.value)}")
                self.conveyorSpeedCallback(event.value)
            # Colour sliders
            if event.ui_element == self.UIElements.get("hue_slider", None):
                colour = self.colourCallback((event.value, None, None))
                self.UIElements["hue_slider_label"].set_text(f"Hue: {event.value}")
                self.update_colour(colour)
            if event.ui_element == self.UIElements.get("saturation_slider", None):
                colour = self.colourCallback((None, event.value, None))
                self.UIElements["saturation_slider_label"].set_text(f"Saturation: {event.value}")
                self.update_colour(colour)
            if event.ui_element == self.UIElements.get("value_slider", None):
                colour = self.colourCallback((None, None, event.value))
                self.UIElements["value_slider_label"].set_text(f"Value: {event.value}")
                self.update_colour(colour)
        # Update the system stats
        if event.type == self.statUpdateEvent:
            cpuUsage = psutil.cpu_percent()
            ramUsage = psutil.virtual_memory().percent
            # Colour thresholds
            cpuColour = self.cpuColour
            if cpuUsage > 80:
                cpuColour = COLOURS["red"]
            elif cpuUsage > 60:
                cpuColour = COLOURS["yellow"]
            else:
                cpuColour = COLOURS["green"]
            if ramUsage > 80:
                ramColour = COLOURS["red"]
            elif ramUsage > 60:
                ramColour = COLOURS["yellow"]
            else:
                ramColour = COLOURS["green"]
            self.UIElements["cpu_usage_label"].set_text(f"{cpuUsage}%")
            self.UIElements["ram_usage_label"].set_text(f"{ramUsage}%")
            if self.cpuColour != cpuColour:
                self.UIElements["cpu_usage_label"].text_colour = pygame.Color(cpuColour)
                self.UIElements["cpu_usage_label"].rebuild()
                self.cpuColour = cpuColour
            if self.ramColour != ramColour:
                self.UIElements["ram_usage_label"].text_colour = pygame.Color(ramColour)
                self.UIElements["ram_usage_label"].rebuild()
                self.ramColour = ramColour
        # Exit Button
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.UIElements.get("exit_button", None):
                self.running = False
            if event.ui_element == self.UIElements.get("enable_button", None):
                self.UIElements["enable_button"].toggle()
            if event.ui_element == self.UIElements.get("offload_inference", None):
                self.UIElements["offload_inference"].toggle()
            if event.ui_element == self.UIElements.get("const_inference", None):
                self.UIElements["const_inference"].toggle()
                self.visionHandler.set_const_inference(self.UIElements["const_inference"].get_value())
            if event.ui_element == self.UIElements.get("inference_once", None):
                self.visionHandler.set_do_inference()
            if event.ui_element == self.UIElements.get("wifi_button", None):
                wifi_restart()
            if event.ui_element == self.UIElements.get("strip_reset_button", None):
                self.stripResetCallback()
            if event.ui_element == self.UIElements.get("take_photo_button", None):
                image = self.cameraFeed.vision.get_frame()
                imageCounter = 0
                while os.path.exists(f"./src/vision/photos/image-{imageCounter:03}.jpg"):
                    imageCounter += 1
                pygame.image.save(image, f"./src/vision/photos/image-{imageCounter:03}.jpg")

    def draw(self) -> None:
        """
        Draw the UI
        """
        self.display.fill(BG_COLOUR)
        self.display.blit(self.cameraSurface, (WIDGET_PADDING, WIDGET_PADDING))
        self.display.blit(self.componentSurface, (LCD_RESOLUTION[0]-self.componentResolution[0]-WIDGET_PADDING, WIDGET_PADDING))
        if not self.trainingMode:
            self.display.blit(self.componentSurface, (LCD_RESOLUTION[0]-self.componentResolution[0]-WIDGET_PADDING, WIDGET_PADDING))

    def update_colour(self, colour) -> None:
        """
        Update the colour string on the display
        """
        hsv = colorsys.rgb_to_hsv(colour[0], colour[1], colour[2])
        rgbColour = [int(x*255) for x in colour]
        hsvColour = [int(x*255) for x in hsv]
        self.UIElements["rgb_colour_code"].set_text(f"RGB: {rgbColour}")
        self.UIElements["hsv_colour_code"].set_text(f"HSV: {hsvColour}")

if __name__ == "__main__":
    TRAININGMODE = False
    INFERENCE = False
    clk = pygame.time.Clock()
    pygame.init()
    vision = Vision_Handler(INFERENCE)
    systemObj = LCD_UI(clk, vision, trainingMode=TRAININGMODE)
    start_ui(
        loopConditionFunc=systemObj.is_running,
        loopFunction=[systemObj.draw],
        eventFunction=[systemObj.handle_events, vision.event_handler],
        exitFunction=[],
        clock=clk,
        manager=systemObj.manager,
        screen=systemObj.display
        )
