# Gimballer camera profiles

The community library of camera profiles for [Gimballer](https://github.com/gimballer/gimballer).
Every copy of Gimballer syncs this repository on launch, so a profile merged
here helps the next operator who flies the same hardware.

A profile tells Gimballer which ExifTool tag holds each standard field for one
camera (Make + Model). See [SCHEMA.md](SCHEMA.md) for the format.

```
profiles/
  DJI/M3T.json
  DJI/ZenmuseP1.json
  Skydio/2+.json
  ...
```

## Contributing a profile

**Easiest: from the app.** Load an image in Gimballer's **Profile Builder**,
check the mapping and save it. Then, on the **Profiles** page, open the
profile's **⋯** menu and choose **Push to GitHub**. Gimballer forks this repo if
needed and opens the pull request for you. This needs a fine-grained Personal
Access Token, set in **Settings › Sharing profiles**. No token? Choose
**Send as GitHub issue** instead and a maintainer will add it.

**By hand:**

1. Run `exiftool -G -n -j your_image.jpg` and find the tags for each field.
2. Create `profiles/<Make>/<Model>.json`, using Make and Model exactly as
   ExifTool reports `EXIF:Make` / `EXIF:Model`. Replace any of `<>:"/\|?*`
   in the file name with `_`.
3. Run `python validate.py`.
4. Open a pull request. CI validates every profile.

### Review checklist

- Coordinates should use the signed `Composite:GPSLatitude` /
  `Composite:GPSLongitude` where the camera writes standard EXIF GPS.
- Gimbal pitch reads about −90 for a straight-down (nadir) image.
- Serial number is the **camera's own serial** (`XMP:CameraSerialNumber` on DJI),
  never the model name or another stand-in, and not the aircraft's serial. If
  the camera records none, map it to `null` and say so in `notes`: Gimballer
  flags those rows `Error: No SerialNumber`. `validate.py` rejects anything else.
- Date is the **capture date** the camera recorded (`EXIF:DateTimeOriginal`
  preferred), never a file date (`File:*`, which is when the file was copied
  or changed). If the camera records none, map it to `null`: Gimballer flags
  those rows `Error: No Date`. `validate.py` rejects file dates.

## Profiles that still need checking against real photos

Fixed on 2026-10-11 (each profile's `notes` says what changed). These still need a photo from
the camera to confirm:

| Profile | What to check |
|---|---|
| `FLIR Systems/XT2.json` | `gimbal_pitch` is now `XMP:GimbalPitchDegree` (it was the lens field of view). Present in FLIR-made images? |
| `DJI/FC2103.json`, `DJI/FC2403.json`, `DJI/ZENMUSE Z30.json` | `serial_number` is now `XMP:CameraSerialNumber` (it was the model name). Does the camera write it? If not, use `null` |
| `DJI/M3E.json`, `DJI/M3TD.json` | `XMP:CameraSerialNumber` assumed from the M3T |
| `DJI/FC2103.json`, `DJI/FC4370.json`, `DJI/ZenmuseP1.json`, `Hasselblad/L2D-20c.json` | `date` is now `EXIF:DateTimeOriginal` (it was `XMP:CreateDate`, which some DJI firmware writes without the time) |
| `DJI/ZH20T.json`, `DJI/FC3170.json`, `DJI/FC4170.json`, `DJI/FC6540.json`, `Hasselblad/L1D-20c.json`, `Hasselblad/L2D-20c.json` | `serial_number` is `EXIF:SerialNumber`: the camera's serial, or the aircraft's? |
| `Phase One/iXM-100.json`, `Parrot/*.json`, `Skydio/*.json` | Does straight down read −90 in their pitch tags? |

## License

MIT
