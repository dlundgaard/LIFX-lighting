import typer
import lifxlan
import sys

MAX_VALUE = 65535 # i.e. 2^16 - 1
COLOR_MAX, COLOR_MIN = 9000, 1500
TRANSITION_DURATION = 1000

lan = lifxlan.LifxLAN(1)
devices = lan.get_lights()
if devices:
    device = devices[0]
else:
    sys.exit("Failed to discover device.")

def turn_on():
    if not device.get_power():
        device.set_power("on")

def turn_off():
    if device.get_power():
        device.set_power("off")

def toggle_power():
    device.set_power("off") if device.get_power() else device.set_power("on")

def set_brightness(level):
    assert 100 >= level >= 0
    device.set_brightness((level / 100) * MAX_VALUE, TRANSITION_DURATION)

def set_color(temp):
    assert COLOR_MAX >= temp >= COLOR_MIN
    device.set_colortemp(temp)

class Scene:
    def __init__(self, color, brightness):
        assert COLOR_MAX >= color >= COLOR_MIN
        assert 100 >= brightness >= 0
        self.color = color
        self.brightness = brightness

    def apply(self):
        turn_on()
        set_color(self.color)
        set_brightness(self.brightness)

    def __repr__(self):
        return f"<Scene(color={self.color}, brightness={self.brightness})>"

scenes = dict(
    cozy = Scene(2500, 37),
    red = Scene(1500, 67),
    bright = Scene(7500, 75),
    blast = Scene(9000, 100)
)

app = typer.Typer()

@app.command()
def toggle():
    toggle_power()

@app.command()
def scene(name: str):
    assert name in scenes, f"{name} is not a saved scene.\n\n" + "Stored scenes:" + "".join(["\n  " + key for key in scenes.keys()])
    scenes[name].apply()

@app.command()
def info(full: bool = False):
    if full:
        typer.echo(device)
    else:
        of_interest = ["MAC Address", "IP Address", "Power", "Location", "Group", "Color (HSBK)"]
        typer.echo("".join(["  " + line + "\n" for line in str(device).split("\n  ") if line.split(":")[0] in of_interest]))

if __name__ == "__main__":
    app()