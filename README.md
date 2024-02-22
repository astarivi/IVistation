# IVistation

### XBMC-Emustation powered OG Xbox emulators frontend

IVistation is an original Xbox project that enhances the functionality and core integration of XBMC-Emustation.
Leveraging XBMC-Emustation by Rocky5 as its base, IVistation refines existing features, and introduces new ones.

Therefore, IVistation provides an emulation frontend for your console, this includes managing roms and artwork,
metadata, and emulation cores. All of this in a simple-to-use and convenient package that acts as a dashboard.

## Index:
 * ### [Installation](docs/guides/Installation.md)
 * ### [Guides and How-tos](docs/guides/README.md)
 * ### [Supported Cores](docs/Cores.tsv)
 * ### [Credits](docs/Credits.md)

# Preview

<p align="center">
    <img src="https://i.ibb.co/4FfbqrZ/1.png" width="98%" />
    <img src="https://i.ibb.co/7vN3r7d/2.png" width="49%" />
    <img src="https://i.ibb.co/v3kTFdf/3.png" width="49%" />
</p>

## Building:

To build IVistation, the following is needed:

- A Linux-like system (MSYS2 MINGW or WSL works too)
- Make
- The latest build of XBMC4XBOX, extracted to the root of the project in a `./XBMC` folder.

Then, build IVistation by running:

```bash
make build
```

A new `./IVistation` folder will be created with the build.
