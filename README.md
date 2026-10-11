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
- Serial number is a real serial. If the camera records none, say so in
  `notes` instead of mapping a different tag.
- Date is a capture date (`EXIF:CreateDate` / `DateTimeOriginal` /
  `XMP:CreateDate`), not a filesystem date (`File:*`), unless the camera
  writes nothing else.

## Profiles imported from Gimballer V2 that need review

These came over unchanged from the V2 library and are worth checking against
real images:

| Profile | Concern |
|---|---|
| `FLIR Systems/XT2.json` | `gimbal_pitch` maps to `APP1:FieldOfView`, which is the lens field of view, not pitch |
| `Hasselblad/[L2D-20c].json` | `gimbal_pitch` maps to `ICC_Profile:ChromaticityColorant`; `serial_number` maps to `EXIF:Model` |
| `DJI/FC2103.json`, `DJI/FC2403.json`, `DJI/MAVIC2-ENTERPRISE-ADVANCED.json`, `DJI/ZENMUSE Z30.json` | `serial_number` maps to `EXIF:Model` |
| `Hasselblad/L3D-100c.json`, `Parrot/AnafiUSA.json` | `date` maps to a filesystem date (`File:FileCreateDate` / `File:FileModifyDate`) |

## License

MIT
