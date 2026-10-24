# Banner options

**Chosen: 3D**, the storm thunderbird (3B shape) in the 3A palette and frame. Implemented in [raijin-scan](https://github.com/protonnegativo/raijin-scan) as `--banner`.

![chosen](3d-thunderbird-storm-violet.png)

The banner is **off by default**. It only prints with an explicit flag (`--banner`), so normal output stays a small JSON. The version number is filled in at runtime from the tool's version constant, so it never needs a manual update.

All art here is original: the dragon, the thunderbird and the bolt are drawn procedurally (`dragon.py`), then converted to braille (2×4 dots per character). `gen.py` renders these previews; the `.txt` files are what the terminal shows.

## 1. Lightning dragon · target-lock HUD (cyan → violet)
![1](1-dragon-hud.png)

## 2. Lightning dragon · Kirin style (white → yellow), no HUD
![2](2-dragon-kirin.png)

## 3. Thunderbird · HUD (amber → orange)
![3](3-thunderbird.png)

### Thunderbird variations

#### 3A. Wings raised · target-lock HUD (cyan → violet)
![3a](3a-thunderbird-hud.png)

#### 3B. Storm: bolts from the wingtips · HUD (amber → orange)
![3b](3b-thunderbird-storm.png)

#### 3C. Totem: Northwest-coast geometric style, eyes on the wings (gold → red)
![3c](3c-thunderbird-totem.png)

## 4. Bolt · compact (white → blue)
![4](4-bolt.png)

## 5. Minimal (least output)
![5](5-minimal.png)
