# Profile schema (v1)

```json
{
  "schema_version": 1,
  "make": "DJI",
  "model": "M3T",
  "fields": {
    "latitude": "Composite:GPSLatitude",
    "longitude": "Composite:GPSLongitude",
    "gimbal_pitch": "XMP:GimbalPitchDegree",
    "serial_number": "XMP:CameraSerialNumber",
    "date": "EXIF:CreateDate",
    "make": "EXIF:Make",
    "model": "EXIF:Model",
    "altitude": null
  },
  "notes": "",
  "contributor": "",
  "updated": "2026-10-10"
}
```

| Key | Type | Notes |
|---|---|---|
| `schema_version` | integer | Always `1` for this format. |
| `make`, `model` | string | Exactly as ExifTool reports them. Matching ignores case and repeated spaces. |
| `fields` | object | Each value is an ExifTool tag as printed with `-G` (`Group:Tag`, family-0 group), or `null` if unmapped. |
| `notes` | string | Anything a reviewer or user should know (firmware quirks, missing serials). |
| `contributor` | string | Optional credit. |
| `updated` | string | ISO date of the last change. |

## Fields

| Field | Required | Output column | How Gimballer reads it |
|---|---|---|---|
| `latitude` | yes | `Latitude` | Signed decimal degrees. DMS strings and XMP `DD,MM.mmN` are converted. `EXIF:GPSLatitude` is signed using `EXIF:GPSLatitudeRef`. |
| `longitude` | yes | `Longitude` | As latitude. |
| `gimbal_pitch` | yes | `GimbalPitchDegree` | Degrees; −90 is straight down. Drives the nadir flag (`IsPoletop`). |
| `serial_number` | no | `SerialNumber` | Text: **the camera's own serial**, from a serial-number tag. Never a stand-in (Make, Model, …) and never the aircraft's serial: DJI enterprise drones write the aircraft serial to `EXIF:SerialNumber` and the camera's to `XMP:CameraSerialNumber`. If the camera records no serial, use `null`. Gimballer then writes `Error: No SerialNumber` in every row; a missing serial is always flagged, never filled in. `validate.py` enforces this. |
| `date` | yes | `Date` | Normalized to `M/D/YYYY  H:MM:SS AM/PM` (wall-clock time as written by the camera). |
| `make`, `model` | no | `Make`, `Model` | Text. If unmapped, the scanned Make/Model are used. |
| `altitude` | no | `Altitude` | Number (e.g. `XMP:AbsoluteAltitude`). |

Tags are read with ExifTool's `-n` option (numeric values), so check yours
with `exiftool -G -n -j image.jpg`.

## Versioning

Gimballer records each profile's git blob SHA in its run history, so an
audited deliverable can always be traced to the exact profile version used.
`.gitattributes` enforces LF line endings so the SHA is the same on every
platform. The `schema_version` field leaves room for future, non-breaking
format changes.
