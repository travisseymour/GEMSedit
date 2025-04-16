"""
GEMSedit: Environment Editor for GEMS (Graphical Environment Management System)
Copyright (C) 2025 Travis L. Seymour, PhD

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from pathlib import Path
from typing import Union, Optional

import sqlite_utils
import yaml
from sqlite_utils import Database


def un_string_lists(text: str) -> str:
    if not isinstance(text, str):
        return text

    if not ("[" in text and "]" in text):
        return text

    txt = text.strip('"').strip("'")
    if txt[0] == "[" and txt[-1] == "]":
        # seems like text defines a list, return a list
        candidate = txt.strip("[").strip("]")
        if "[" in candidate or "]" in candidate:
            return text  # something is fishy here...too many brackets to handle
        candidate = candidate.split(",")
        candidate = [
            (
                eval(item)
                if str(item).isdigit()
                else f"""{str(item).strip('"').strip("'")}"""
            )
            for item in candidate
        ]
        return str(candidate).replace(", ", ",")
    else:
        # seems like text that *contains* a list definition. return a cleanup up string
        txt = txt.replace('"[', "[").replace(']"', "]")
        txt = txt.replace("'[", "[").replace("]'", "]")
        return txt


def sqlite_to_dict(db_file: Union[Path, str], env_name: Optional[str] = None) -> dict:
    db = sqlite_utils.Database(db_file)

    # print(db.schema)
    # print('=====================')
    #
    # pprint(db['views'].columns)
    # pprint(db['global'].columns)
    # pprint(db.tables)
    """
    [<Table objects (Id, Parent, Name, Left, Top, Width, Height, Visible, Takeable, RowOrder)>,
     <Table actions (Id, ContextType, ContextId, Condition, Trigger, Action, Enabled, RowOrder)>,
     <Table views (Id, Name, Foreground, Background, Overlay, RowOrder)>,
     <Table options (Id, Startview, Pocketcount, Roomtransition, Preloadresources, Globaloverlay, Version, StageColor, DisplayType, ObjectHover)>,
     <Table condition_lst (Id, Name, Template, Labels, Restrictions)>,
     <Table trigger_lst (Id, Name, Template, Labels, Restrictions)>,
     <Table action_lst (Id, Name, Template, Labels, Restrictions)>]
    """

    # init dict db
    dict_db = dict()
    dict_db["Name"] = (
        Path(db_file).stem.title()
        if not isinstance(env_name, str)
        else env_name.strip()
    )
    dict_db["Id"] = 0

    options = [k for k in db["options"].rows][0]

    # convert and listy strings to actual lists
    options = {
        key: un_string_lists(value) if isinstance(value, str) else value
        for key, value in options.items()
    }

    # convert version to strings
    options["Version"] = str(options["Version"])

    # add volume to options
    if "Volume" not in options:
        options["Volume"] = 1.0

    # add global options info
    dict_db["Global"] = {}

    # add newly altered options
    dict_db["Global"]["Options"] = options

    # add global actions
    dict_db["Global"]["GlobalActions"] = {}
    for action in db["actions"].rows_where(f'ContextType == "global"'):
        action["Action"] = un_string_lists(action["Action"])
        # action['Enabled'] = bool(action['Enabled'])   # instead, convert when used
        dict_db["Global"]["GlobalActions"][str(action["Id"])] = action

    # add pocket actions
    dict_db["Global"]["PocketActions"] = {}
    for action in db["actions"].rows_where(f'ContextType == "pocket"'):
        action["Action"] = un_string_lists(action["Action"])
        # action['Enabled'] = bool(action['Enabled'])   # instead, convert when used
        dict_db["Global"]["PocketActions"][str(action["Id"])] = action

    # add views
    dict_db["Views"] = {}
    for view in db["views"].rows:

        # add view actions
        view["Actions"] = {}
        for action in db["actions"].rows_where(
            f'ContextType == "view" and ContextId == {view["Id"]}'
        ):
            action["Action"] = un_string_lists(action["Action"])
            # action['Enabled'] = bool(action['Enabled'])   # instead, convert when used
            view["Actions"][str(action["Id"])] = action

        # add view objects
        view["Objects"] = {}
        for obj in db["objects"].rows_where(f'Parent == {view["Id"]}'):

            # update draggable is needed
            if "Draggable" not in obj:
                obj["Draggable"] = obj["Takeable"]

            # add view object actions
            obj["Actions"] = {}
            for action in db["actions"].rows_where(
                f'ContextType == "object" and ContextId == {obj["Id"]}'
            ):
                action["Action"] = un_string_lists(action["Action"])
                # action['Enabled'] = bool(action['Enabled'])   # instead, convert when used
                obj["Actions"][str(action["Id"])] = action

            view["Objects"][str(obj["Id"])] = obj

        # remove nulls in Overlay
        if "Overlay" in view and view["Overlay"] is None:
            view["Overlay"] = ""

        # finally, store views
        dict_db["Views"][str(view["Id"])] = view

    # condition_lst
    dict_db["condition_lst"] = {}
    for row in db["condition_lst"].rows:
        dict_db["condition_lst"][str(row["Id"])] = row

    # trigger_lst
    dict_db["trigger_lst"] = {}
    for row in db["trigger_lst"].rows:
        dict_db["trigger_lst"][str(row["Id"])] = row

    # action_lst
    dict_db["action_lst"] = {}
    for row in db["action_lst"].rows:
        dict_db["action_lst"][str(row["Id"])] = row

    return dict_db


def load_yaml_as_dict(
    yaml_file: Union[str, Path], extra_yaml: Optional[Union[str, Path]] = None
) -> dict:
    with open(yaml_file, "r") as infile:
        db_dict = yaml.safe_load(infile)

    if extra_yaml is not None:
        with open(extra_yaml, "r") as infile:
            extra_dict = yaml.safe_load(infile)
        db_dict = {**db_dict, **extra_dict}

    return db_dict


def dict_to_sqlite_file(
    db: dict, db_file_name: Union[str, Path], overwrite: bool = False
) -> Path:
    """Automatically saves to disk as sqlite db is constructed from the dict. Returns path of sqlite db."""
    db_path = Path(db_file_name)
    sql_db = Database(db_path, recreate=overwrite)

    """
    what we got from original sqlitedb schema [KEEP HERE]
    [<Table objects (Id, Parent, Name, Left, Top, Width, Height, Visible, Takeable, RowOrder)>,
     <Table actions (Id, ContextType, ContextId, Condition, Trigger, Action, Enabled, RowOrder)>,
     <Table views (Id, Name, Foreground, Background, Overlay, RowOrder)>,
     <Table options (Id, Startview, Pocketcount, Roomtransition, Preloadresources, Globaloverlay, Version, 
                     StageColor, DisplayType, ObjectHover)>,
     <Table condition_lst (Id, Name, Template, Labels, Restrictions)>,
     <Table trigger_lst (Id, Name, Template, Labels, Restrictions)>,
     <Table action_lst (Id, Name, Template, Labels, Restrictions)>]
    """

    schema_commands = [
        "CREATE TABLE objects(Id INT PRIMARY KEY UNIQUE, Parent INT, Name TEXT, Left INT, Top INT, Width INT, Height INT, Visible INT, Takeable INT, Draggable INT, RowOrder INT);",
        "CREATE TABLE actions(Id INT PRIMARY KEY UNIQUE, ContextType TEXT, ContextId INT, Condition TEXT, Trigger TEXT, Action TEXT, Enabled boolean, RowOrder INT);",
        "CREATE TABLE views(Id INT PRIMARY KEY UNIQUE, Name TEXT UNIQUE, Foreground TEXT, Background TEXT, Overlay TEXT, RowOrder INT);",
        "CREATE TABLE options(Id INT PRIMARY KEY UNIQUE, Startview INT, Pocketcount INT,  Roomtransition TEXT, Preloadresources INT, Globaloverlay TEXT, Version TEXT, StageColor TEXT, DisplayType TEXT, ObjectHover TEXT, Volume REAL);",
        "CREATE TABLE condition_lst(Id INT PRIMARY KEY UNIQUE, Name TEXT, Template TEXT, Labels TEXT, Restrictions TEXT );",
        "CREATE TABLE trigger_lst(Id INT PRIMARY KEY UNIQUE, Name TEXT, Template TEXT, Labels TEXT, Restrictions TEXT );",
        "CREATE TABLE action_lst(Id INT PRIMARY KEY UNIQUE, Name TEXT, Template TEXT, Labels TEXT, Restrictions TEXT );",
    ]

    for aline in schema_commands:
        sql_db.execute(aline)

    def arrange_action(action: dict) -> dict:
        return {
            "Id": action["Id"],
            "ContextType": action["ContextType"],
            "ContextId": action["ContextId"],
            "Condition": action["Condition"],
            "Trigger": action["Trigger"],
            "Action": action["Action"],
            "Enabled": action["Enabled"],
            "RowOrder": action["RowOrder"],
        }

    # collect and add actions to actions-table
    actions = list()
    if db["Global"]["GlobalActions"]:
        for action in db["Global"]["GlobalActions"].values():
            # actions.append(action)
            actions.append(arrange_action(action))
    if db["Global"]["PocketActions"]:
        for action in db["Global"]["PocketActions"].values():
            actions.append(arrange_action(action))
    for view in db["Views"].values():
        # view actions
        for action in view["Actions"].values():
            actions.append(arrange_action(action))
        # view object actions
        for obj in view["Objects"].values():
            for obj_action in obj["Actions"].values():
                actions.append(arrange_action(obj_action))
    # pprint(actions, width=500)
    sql_db["actions"].insert_all(actions)

    # collect and add objects to objects-table
    objects = list()
    for view in db["Views"].values():
        # view objects
        for obj in view["Objects"].values():
            try:
                del obj["Actions"]
            except KeyError:
                ...
            objects.append(obj)
    sql_db["objects"].insert_all(objects)

    # collect views and remove keys for actions and objects
    # WARNING: This might alter the views in the dict, don't process anything in views after this section
    views = list()
    for view in db["Views"].values():
        try:
            del view["Actions"]
            del view["Objects"]
        except KeyError:
            ...
        views.append(view)
    sql_db["views"].insert_all(views)

    # other misc tables
    sql_db["options"].insert(db["Global"]["Options"])
    sql_db["condition_lst"].insert_all(db["condition_lst"].values())
    sql_db["trigger_lst"].insert_all(db["trigger_lst"].values())
    sql_db["action_lst"].insert_all(db["action_lst"].values())

    # for row in sql_db['condition_lst'].rows:
    #     print(row)

    return db_path


if __name__ == "__main__":
    # test_sqlite_to_dict
    db_file = Path(
        Path.home(),
        "Dropbox",
        "Documents",
        "python_coding",
        "GEMS_2021",
        "KidsRoom",
        "kidsroom.db",
    )
    db_file_xxx = Path(
        Path.home(),
        "Dropbox",
        "Documents",
        "python_coding",
        "GEMS_2017",
        "KidsRoom",
        "kidsroom.db",
    )
    db_as_dict = sqlite_to_dict(db_file_xxx)

    # pprint(db_as_dict)
    new_yaml_file = Path(Path(db_file).parent, Path(db_file).stem + "_y2s2y.yaml")
    new_yaml_file_xxx = Path(Path(db_file).parent, Path(db_file).stem + ".yaml")

    with open(new_yaml_file, "w") as outfile:
        yaml.dump(db_as_dict, outfile, default_flow_style=False)
    with open(new_yaml_file_xxx, "w") as outfile:
        yaml.dump(db_as_dict, outfile, default_flow_style=False)

    # test dict_to_sqlite
    new_db_file = Path(Path(db_file).parent, Path(db_file).stem + "_y2s2y.db")
    db_as_dict_from_disk = load_yaml_as_dict(new_yaml_file)

    sqlite_db_file = dict_to_sqlite_file(
        db_as_dict_from_disk, new_db_file, overwrite=True
    )
