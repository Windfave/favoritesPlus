
# favoritesPlus

favoritesPlus is a simple webapp that lets you store all your favourite gifs. This has been made because Discord has the limit 1299 favourite gifs. I had 3.3k favourite gifs for years, and not being able to favourite new gifs was frustrating. Hence why I made favoritesPlus.

For now, favoritesPlus supports:
- ✅ **discord cdn gifs** (although, discord links expire after 24 hours, so it's not really recommended.)
- ✅ **direct gif links**
- ✅ **tenor gifs** (link must be without a country code format)

Some current issues:
- ❌ **giphy gifs**
- ❌ **If you load all gifs over time, memory leak happens. (Gotta fix pagination so gifs render only in viewport)**
- ❌ **discord gifs expiring after a day (already mentioned above.)** (Currently, it's better to upload your discord gifs elsewhere and import them that way. Make sure the url is a direct link to the gif file.)

Some plans:
- ℹ️ **better rendering system to not have memory leak issues**
- ℹ️ **turn into either a vencord/betterdiscord plugin or an electron webapp**
- ℹ️ **possibly be able to load entire page at once but only render ones near the viewport**
- ℹ️ **giphy and imgur gif support**


## Installation

You need Python 3.12.4 and above.
The requirements are as follows:

- beautifulsoup4==4.13.3
- Flask==3.1.0
- Requests==2.32.3

```bash
  cd drive://path-to/favoritesPlus
  pip install <requirement>
```
To run the project, you execute the following command:
```bash
  python app.py 
```
Now, you will be able to go to 127.0.0.1:5000 and view the project.
