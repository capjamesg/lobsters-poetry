# lobsters-poetry

Poetry generated programmatically from the front page of Lobste.rs. Reset hourly.

[View the latest poems](https://lobsterspoetry.jamesg.blog).

## Examples

- from Lobste.rs, I learned framework
- my look is manual
- an atomic Lobste.rs
- in 2001, fidelity
- be single and single
- the programmatic llms of challenge
--

(Generated from the homepage on March 3rd, 2024)

## Installation

To install this software, run:

```
git clone https://github.com/capjamesg/lobsters-poetry
cd lobsters-poetry/
pip3 install tracery flair requests tqdm jinja2
```

To generate poems, run:

```
python3 hn.py
```

The script retrieves new titles and generates poems.

For testing, comment out the `get_front_page()` function call once you have run the script once. This will allow you to generate poems without retrieving the homepage and its associated titles for each time you run the script.

## License

This project is licensed under an [MIT license](LICENSE).
