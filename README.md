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
> Only osu!standard is currently supported.

## Getting Started
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

> Go to your [osu! settings page](https://osu.ppy.sh/home/account/edit) and click "New OAuth Application" near the bottom, give it any name you want, and add "http://localhost:7270/" as a callback URL.
>
> Under the "Legacy API" tab, create an API key if you haven't already.
>
> Rename or copy `.example.env` to `.env` and fill it out with your API key, client ID, and client secret.

**Run the script:**
> ```
> python scorepostgenerator.py
> ```
> The first time you run the script (or if you haven't run it in a while), it will make you authenticate on the osu! website.

## Contributing
I don't have a clue what I'm doing so pull requests are open if you notice any glaring flaws in my code.

## Acknowledgements
- [tybug](https://github.com/tybug) for [ossapi](https://github.com/tybug/ossapi) and [Circlecore](https://github.com/circleguard/circlecore), used for everything to do with the API and UR calculation
- [Sheppsu](https://github.com/Sheppsu) for [osu.py](https://github.com/Sheppsu/osu.py), used for non-legacy API functions
- [MaxOhn](https://github.com/MaxOhn) for [rosu-pp](https://github.com/MaxOhn/rosu-pp), used for PP calculation
