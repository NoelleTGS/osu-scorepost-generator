# osu! Scorepost Generator
A generator for r/osugame-styled osu! scoreposts.
### Features
- Generate scorepost title using osu!'s API
- Get score info using score ID, or by entering a username/user ID
- Calculate PP for FC if score isn't an FC
- Supports ranked, loved, and graveyarded maps
- Calculate UR of plays with replays
- Automatically copy title to your clipboard, and optionally open r/osugame submission page

> [!NOTE]
> All modes are supported, but modes other than osu!standard might be missing features or have bugs. Feel free to report any problems in the issues tab.

## Usage
> [!IMPORTANT]
> Before starting, make sure you have created an API key and an OAuth application on the osu! website.
> <details>
> <summary>Instructions</summary>
> 
> Go to your <a href="https://osu.ppy.sh/home/account/edit">osu! settings page</a> and click "New OAuth Application" near the bottom, give it any name you want, and add "http://localhost:7270/" as a callback URL.
> Copy the client ID and client secret for later.
> 
> 
> Under the "Legacy API" tab, create an API key.
> The application name and URL can be whatever you like. Copy the API key for later.
> </details>

### Binary
Download the latest binary from the [releases tab](https://github.com/NoelleTGS/osu-scorepost-generator/releases) according to your platform.

**Windows:**
1. Extract the zip file.
2. Make a copy of the `.example.env` file and rename it to `.env`.
3. Open `.env` in your favourite text editor and fill in your osu! API key, and the client ID and secret from the OAuth app you made earlier.
4. Run the `scorepostgenerator.exe` file.
   - The first time you run the script (or if you haven't run it in a while), it will make you authenticate on the osu! website.

**Linux:** 
1. Extract the zip file and copy the `.example.env` file to `.env`.
    ```shell
    unzip scorepostgenerator-linux.zip
    cd scorepostgenerator-linux
    cp .example.env .env
    ```
2. Open `.env` in your favourite text editor and fill in your osu! API key, and the client ID and secret from the OAuth app you made earlier.
3. Make the `scorepostgenerator` file executable and run it. 
    - The first time you run the script (or if you haven't run it in a while), it will make you authenticate on the osu! website.
    ```shell
    chmod +x scorepostgenerator
    ./scorepostgenerator
    ```
### From source
**Clone the repository:**
> ```
> git clone https://github.com/NoelleTGS/osu-scorepost-generator.git
> cd osu-scorepost-generator
> ```
**Install dependencies:**
> ```
> pip install -r requirements.txt
> ```
**Set up environment variables:**
> Rename or copy `.example.env` to `.env` and fill it out with your API key, client ID, and client secret.

**Run the script:**
> ```
> python scorepostgenerator.py
> ```
> The first time you run the script (or if you haven't run it in a while), it will make you authenticate on the osu! website.

### Command line arguments
If you're a poweruser, you can run the script using command line arguments.
```
usage: scorepostgenerator.py [-h] [-v] -m MODE (-u USER | -s SCORE) [-b | -r] [-nf]

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -m MODE, --mode MODE  The mode of the score you wish to retrieve.
  -u USER, --user USER  The username of the player whose score you wish to retrieve.
  -s SCORE, --score SCORE
                        The ID of the score you wish to retrieve.
  -b, --best            Retrieve the best score.
  -r, --recent          Retrieve the recent score.
  -nf, --nofails        Don't count fails when getting recent score.
```
This works on both the `.py` file and the packaged build from the releases tab.

## Important Info
> [!NOTE]
> In osu!standard, as there is still no way to reliably differentiate between an S-rank with sliderbreaks and an FC with missed sliderends (tracked in https://github.com/NoelleTGS/osu-scorepost-generator/issues/10), an approximation is made where if the max combo of the play is more than 99% of the max combo of the beatmap, the score is counted as an FC. I have found very few instances where this ends up being incorrect, but if you find any more or know a better way to do this, feel free to post in the linked issue.

## Contributing
I don't have a clue what I'm doing so pull requests are open if you notice any glaring flaws in my code.

## Acknowledgements
- [tybug](https://github.com/tybug) for [ossapi](https://github.com/tybug/ossapi) and [Circlecore](https://github.com/circleguard/circlecore), used for everything to do with the API and UR calculation
- [Sheppsu](https://github.com/Sheppsu) for [osu.py](https://github.com/Sheppsu/osu.py), used for non-legacy API functions
- [MaxOhn](https://github.com/MaxOhn) for [rosu-pp](https://github.com/MaxOhn/rosu-pp), used for PP calculation
