import webbrowser
import pathlib
import subprocess
import datetime
import json


TEMPLATE = """
<!doctype html>
<html>

<head>
    <style>
        figure{{
            display: inline-block;
        }}
    </style>
    <title>Grow Evolution</title>
</head>

<body>
    <h1>Grow Evolution</h1>
    {figures}
</body>
</html>
"""

FIGURETEMPLATE = """
    <figure>
        <img src="{image}", alt="{date}" title="{date}"/>
        <figcaption>Day {label}</figcaption>
    </figure>
"""

if __name__ == "__main__":
    # read all IMG*.jpg in folder images
    infilelist = sorted(pathlib.Path(__file__).parent.joinpath("images").glob("IMG*.jpg"), reverse=True)
    outfiledict = dict()
    for infilename in infilelist:
        # extract date and time from image name
        date = datetime.datetime(
            year=int(infilename.stem[4:8]),
            month=int(infilename.stem[8:10]),
            day=int(infilename.stem[10:12]),
            hour=int(infilename.stem[13:15]),
            minute=int(infilename.stem[15:17]),
            second=int(infilename.stem[17:19]),
        )
        # resize image and store it under new name with prefix 'r_'##
        outfilename = pathlib.Path.joinpath(infilename.parent, f"r_{infilename.name}")
        if outfilename.exists():
            print(f"{str(outfilename)} already exists")
        else:
            subprocess.run(["convert", infilename, "-resize", "400x", outfilename])
        # store all images along with date in dictionary
        outfiledict[str(outfilename)] = dict(date=date)

    lastimage = list(outfiledict.keys())[-1]
    print(f"lastimage={lastimage}")

    for index, name in enumerate(outfiledict):
        # calculate the day of image with respect to the date of lastimage
        if name == lastimage:
            outfiledict[name]["days"] = 0
        else:
            tdiff = outfiledict[name]["date"] - outfiledict[lastimage]["date"]
            outfiledict[name]["days"] = tdiff.days

    # enable only if you need to rewrite it really. Edit later to fix labels
    if 0:
        odict = dict()
        for name, value in outfiledict.items():
            odict[name] = dict(date=str(value["date"]), label=value["days"])
        with open("build.json", "w") as fh:
            json.dump(odict, fh, indent=4)

    # open the database with all images
    with open("build.json", "r") as fh:
        odict = json.load(fh)

    # insert new mages in database
    for name, value in outfiledict.items():
        if name in odict:
            continue
        odict[name] =  dict(date=str(value["date"]), label=value["days"])

    # sort images in database
    odict = dict(sorted(odict.items(), reverse=True))
    # save database
    with open("build.json", "w") as fh:
        json.dump(odict, fh, indent=4)

    # generate html code for figures
    figurelist = list()
    for index, name in enumerate(odict):
        value = odict[name]
        figurelist.append(FIGURETEMPLATE.format(image=name, date="{} (Week {})".format(value["date"], value["label"] // 7 + 1), label=value["label"], ))
        if index % 3 == 2:
            figurelist.append("<br/>")

    # generate html code
    with open("evolution.html", "w") as fh:
         print(TEMPLATE.format(figures="\n".join(figurelist)), file=fh)
    print(f"written file {fh.name}")

    webbrowser.open("evolution.html")
