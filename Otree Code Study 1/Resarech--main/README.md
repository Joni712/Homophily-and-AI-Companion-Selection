# Project layout

-   `pilot/`: pilot app, with part 1 or experiment in single round
-   `main/`: full app, with 3 parts in 5 rounds (3 parts + fake begining, ending rounds)
-   `utils/`: various utils used in the apps
-   `data/`: data files
    -   `bots.csv`: description of bots `id,section,gender,race,name` (names only for part3)
    -   `names.csv`: list of names for bots `gender,name`
    -   `tasks.csv`: all the tasks `section,question,A,B,C,D,correct`
    -   `simulated.csv`: result data simulated from analogous experiment, should contain column `score`
    -   `results.csv`: participants' results from pilot, should contain column `player.score`
-   `_templates/`: html templates for pages
-   `_static/`: scripts and styles
