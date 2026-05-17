import pyglet, time
import pyglet.gl as gl
from pyglet import window
from activity_recognizer import ActivityRecognizer


class ActivityDisplay:
    def __init__(self, box):
        self.box = box
        self.labels = pyglet.graphics.Batch()
        self.activity_images = None
        self.unknown_activity_text = "Unknown Exercise or Incorrect Form"
        self.create_labels()
        self.create_icons()

    def create_labels(self):
        self.title_label = pyglet.text.Label(
            "DETECTED ACTIVITY",
            font_size=int(self.box.height * 0.02),
            x=self.box.width / 2,
            y=self.box.height * 0.95,
            anchor_x="center",
            color=(255, 255, 255, 255),
            batch=self.labels,
        )
        self.activity_label = pyglet.text.Label(
            "NO SENSOR",
            font_size=int(self.box.height * 0.05),
            x=self.box.width / 2,
            y=self.box.height * 0.89,
            anchor_x="center",
            color=(77, 217, 100, 255),
            batch=self.labels,
        )
        self.confidence_label = pyglet.text.Label(
            "CONFIDENCE SCORE",
            font_size=int(self.box.height * 0.02),
            x=self.box.width / 2,
            y=self.box.height * 0.25,
            anchor_x="center",
            color=(255, 255, 255, 255),
            batch=self.labels,
        )
        self.confidence_score_label = pyglet.text.Label(
            "N/A",
            font_size=int(self.box.height * 0.03),
            x=self.confidence_label.x - self.confidence_label.content_width / 2,
            y=self.box.height * 0.20,
            anchor_x="left",
            color=(77, 217, 100, 255),
            batch=self.labels,
        )
        self.time_in_activity_label = pyglet.text.Label(
            "TIME IN ACTIVITY:",
            font_size=int(self.box.height * 0.02),
            x=self.confidence_label.x - self.confidence_label.content_width / 2,
            y=self.box.height * 0.15,
            anchor_x="left",
            color=(255, 255, 255, 255),
            batch=self.labels,
        )
        self.time_in_activity_value_label = pyglet.text.Label(
            "0s",
            font_size=int(self.box.height * 0.03),
            x=self.time_in_activity_label.x,
            y=self.box.height * 0.10,
            anchor_x="left",
            color=(77, 217, 100, 255),
            batch=self.labels,
        )

        self.loading_label = pyglet.text.Label(
            "Loading the Fitness Trainer...",
            font_size=int(self.box.height * 0.07),
            x=self.box.width / 2,
            y=self.box.height * 0.6,
            anchor_x="center",
            color=(0, 10, 10, 255),
            batch=self.labels,
        )

    def create_icons(self):
        self.icons = pyglet.graphics.Batch()
        self.confidence_icon = pyglet.sprite.Sprite(
            pyglet.image.load("img/circle-check.png"), batch=self.icons
        )
        self.confidence_icon.scale = 0.5
        self.confidence_icon.x = (
            self.confidence_score_label.x
            - self.confidence_score_label.content_width / 2
            - 50
            - self.confidence_icon.width / 2
        )
        self.confidence_icon.y = self.confidence_score_label.y - 20

        self.time_icon = pyglet.sprite.Sprite(
            pyglet.image.load("img/stopwatch.png"), batch=self.icons
        )
        self.time_icon.scale = 0.5
        self.time_icon.x = self.confidence_icon.x
        self.time_icon.y = self.time_in_activity_value_label.y - 20

    def update_display(self, activity, confidence):
        self.activity_label.text = activity
        self.confidence_score_label.text = f"{confidence * 100:.1f}%"
        self.get_activity_images(activity)

    def get_activity_images(self, activity):
        if activity == self.unknown_activity_text:
            self.activity_images = None
            return
        name = activity.lower().replace(" ", "")
        f1 = f"img/{name}_1.png"
        f2 = f"img/{name}_2.png"
        try:
            self.activity_images = [pyglet.image.load(f1), pyglet.image.load(f2)]
        except FileNotFoundError as e:
            print(f"Error loading images for {activity}: {e}")

    def on_draw(self):
        self.labels.draw()
        self.icons.draw()
        if self.activity_images:
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(
                gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA
            )  # pylint: disable=unreachable

            img1 = self.activity_images[0]
            img2 = self.activity_images[1]

            spacing = int(self.box.height * 0.04)
            max_image_height = self.box.height * 0.4
            max_total_width = self.box.width * 0.72

            scale_by_height = max_image_height / max(img1.height, img2.height)
            scale_by_width = max_total_width / (img1.width + spacing + img2.width)

            scale = min(scale_by_height, scale_by_width)

            w1 = img1.width * scale
            h1 = img1.height * scale
            w2 = img2.width * scale
            h2 = img2.height * scale

            total_width = w1 + spacing + w2
            start_x = (self.box.width - total_width) / 2

            y = self.box.height / 2 - max(h1, h2) / 2 + 100

            img1.blit(start_x, y, width=w1, height=h1)
            img2.blit(start_x + w1 + spacing, y, width=w2, height=h2)
            
       


class Trainer:
    def __init__(self, window):
        self.background = pyglet.image.load("img/bg1.png")
        self.window = window
        self.current_activity = None
        self.confidence = None
        self.activity_display = ActivityDisplay(self.window)
        self.timer = 0
        self.timer_start = time.time()

    def set_activity(self, activity, confidence):
        if self.current_activity != activity:
            self.restart_timer()
        self.current_activity = activity
        self.confidence = confidence
        self.update_display()

    def restart_timer(self):
        self.timer = 0
        self.timer_start = time.time()

    def update_timer(self):
        if self.current_activity is not None:
            self.timer = round((time.time() - self.timer_start),1)
            self.activity_display.time_in_activity_value_label.text = f"{self.timer}s"
        

    def update_display(self):
        self.activity_display.update_display(self.current_activity, self.confidence)

    def draw(self):
        self.background.blit(0, 0, width=self.window.width, height=self.window.height)
        self.update_timer()
        self.activity_display.on_draw()


def main():
    window = pyglet.window.Window(2000, 1400, "Activity Trainer")

    trainer = Trainer(window)

    recognizer = ActivityRecognizer()

    def startup(dt):
        recognizer.prepare_recognizer()
        recognizer.start_recognizer()
        trainer.activity_display.loading_label.color = (0, 0, 0, 0)

    pyglet.clock.schedule_once(startup, 0.1)

    @window.event
    def on_draw():
        window.clear()
        trainer.draw()

    @window.event
    def on_close():
        recognizer.stop_recognizer()
        pyglet.app.exit()

    pyglet.clock.schedule_interval(
        lambda dt: query_activity_prediction(dt, trainer, recognizer), 0.5
    )


def query_activity_prediction(dt, trainer, recognizer):
    activity = recognizer.get_prediction()
    if activity is None:
        return
    confidence = recognizer.get_confidence()
    if confidence is None:
        return
    # if confidence < 0.72:
    #   activity = trainer.activity_display.unknown_activity_text
    trainer.set_activity(activity, confidence)


if __name__ == "__main__":
    main()
    pyglet.app.run()
