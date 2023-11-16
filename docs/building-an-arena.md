# Building an arena

This tutorial will take you through the process of building a basic arena for conducting touchscreen-based behavioural assays in freely moving mice. The arena will be built using a Raspberry Pi 4, a Hyperpixel 4.0 touchscreen, and a few other components. The total cost of the arena is roughly £500 at the time of writing, and can be built in a few hours assuming you have access to the required tools. The arena is designed to be as simple as possible to build, and can be easily modified to suit your needs.

!!! note
    While this guide describes building an arena for freely moving mice, the same principles can be applied to building an arena for freely moving rats - only difference is that the arena will need to be larger to accommodate their size. The [official 7" Raspberry Pi touchscreen](https://www.raspberrypi.org/products/raspberry-pi-touch-display/) is a good option for a rat-sized setup.

## What you'll need

For the arena itself, you will need:

- 1x [3mm red tint acrylic sheet](https://www.sheetplastics.co.uk/3mm-red-tint-acrylic-sheet-cut-to-size) cut to 200mm x 250mm.
- 1x [3mm red tint acrylic sheet](https://www.sheetplastics.co.uk/3mm-red-tint-acrylic-sheet-cut-to-size) cut to 400mm x 250mm.
- 2x [5mm black acrylic sheets](https://www.sheetplastics.co.uk/5mm-black-acrylic-sheet-cut-to-size) cut to 200mm x 250mm.
- 2x [5mm black acrylic sheets](https://www.sheetplastics.co.uk/5mm-black-acrylic-sheet-cut-to-size) cut to 400mm x 250mm.
- 2x [5mm black acrylic sheets](https://www.sheetplastics.co.uk/5mm-black-acrylic-sheet-cut-to-size) cut to 400mm x 200mm.
- 2x [3mm clear acrylic sheets](https://www.sheetplastics.co.uk/3mm-clear-acrylic-sheet-cut-to-size) cut to 100mm x 150mm.
- 4x [aluminium profile struts, 20 x 20 mm, 5mm groove, 1000mm length](https://uk.rs-online.com/web/p/tubing-and-profile-struts/8508476?gb=s) (or equivalent).
- 10x [angle bracket connecting components for strut profile 20 mm, groove size 5mm](https://uk.rs-online.com/web/p/connecting-components/1809136?gb=s) (or equivalent).
- A box of [M4 x 8mm hex socket cap screws](https://uk.rs-online.com/web/p/socket-screws/4679852?gb=s).
- A box of [M4 x 10mm hex socket cap screws](https://uk.rs-online.com/web/p/socket-screws/4679874?gb=s).
- A box of [M4 x 20mm hex socket cap screws](https://uk.rs-online.com/web/p/socket-screws/4679903?gb=s).
- 40x [M4 T-slot nut connecting components for strut profile 20 mm, groove size 5mm](https://uk.rs-online.com/web/p/connecting-components/1809106?gb=s).
- 4x [magnetic tape strips](https://uk.rs-online.com/web/p/magnetic-tapes/0846339?gb=s).
- A pair of [150mm stainless steel rulers](https://uk.rs-online.com/web/p/rulers/2197001?gb=s).
- (Optional) [Sound-proofing foam sheets](https://uk.rs-online.com/web/p/acoustic-insulation/0293142?gb=s), if you're planning to use the arena in a noisy environment.

For the touchscreen module, you will need:

- A [Raspberry Pi 4](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) with Visiomode installed (see [Getting started](index.md)).
- A [Hyperpixel 4.0 touchscreen](https://shop.pimoroni.com/products/hyperpixel-4).
- 2x [mounting brackets with screw holes](https://uk.rs-online.com/web/p/enclosure-mounting/7491686?gb=s). These are optional but recommended, as they will make it easier to mount the touchscreen to the arena.
- A box of [M2.5 x 6mm hex socket cap screws](https://uk.rs-online.com/web/p/socket-screws/4733423?gb=s).
- A bag of [M2.5 nylon washers](https://uk.rs-online.com/web/p/washers/2326898?gb=s).

For the reward system, you will need:

- An [Arduino Nano](https://store.arduino.cc/products/arduino-nano) (or equivalent microcontroller).
- A [miniature 5V solenoid valve](https://www.amazon.co.uk/dp/B07VLW5FTD/ref=sspa_dk_detail_4?psc=1&pd_rd_i=B07VLW5FTD&pd_rd_w=s46ZF&content-id=amzn1.sym.84ea1bf1-65a8-4363-b8f5-f0df58cbb686&pf_rd_p=84ea1bf1-65a8-4363-b8f5-f0df58cbb686&pf_rd_r=7GBV4VK4SCAV5XZ4HGCZ&pd_rd_wg=QdAGE&pd_rd_r=cd42e971-4676-4cb5-b177-0adfc4fca472&s=diy&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWw) (or equivalent).
- A [5V servo motor](https://thepihut.com/products/towerpro-servo-motor-sg90-digital) (or equivalent).
- A variety of [single core hook up wires](https://uk.rs-online.com/web/p/hook-up-wire/8840869?gb=s) (red/black/green or similar).
- [Plastic flexible tubing](https://uk.rs-online.com/web/p/hose-pipe-flexible-tubes/6678444?gb=s) with an internal diameter of 4mm.
- An [18G dispensing needle tip](https://www.digikey.co.uk/en/products/detail/apex-tool-group/KDS181P/4525142).
- (Optional) A small [Noga arm](https://uk.rs-online.com/web/p/bases-arms/7857844). This is optional but recommended, as it will make it _much_ easier to mount the reward system to the arena.

You will also need access to the following equipment:

- A hot glue gun.
- A soldering station.
- A drill (any will do but a standing drill is recommended).
- A jigsaw (or hand saw if you have a lot of patience), with blades suitable for cutting through metal and plastic.
- A laser cutter (or a CNC router) capable of cutting 3mm and 5mm acrylic sheets. This is required for the slit inserts that facilitate forelimb reaching responses described by [Eleftheriou et al. 2023](https://doi.org/10.1016/j.jneumeth.2022.109779). If you don't have access to a laser cutter / CNC machine you might want to consider outsourcing this task to an external vendor such as [Get It Made](https://get-it-made.co.uk) or [Protolabs](https://www.protolabs.com/en-gb/services/cnc-machining/), but always check with your local University / Institute workshop / Engineering department first as they may be able to do this for you. Other than the slit inserts, the rest of the arena can be built using a jigsaw, a drill and a hot glue gun.

!!! warning
    This tutorial assumes you have some basic knowledge of electronics and soldering, and are comfortable using a soldering iron. If you are not, please seek help from someone who is.
    Alternatively, you can use a [breadboard](https://learn.sparkfun.com/tutorials/how-to-use-a-breadboard/all) to assemble the electronics, but this is not recommended for a permanent setup.

## Assembling the electronics


## Putting the arena together


## Calibrating the reward system


## Testing the arena


## Next steps