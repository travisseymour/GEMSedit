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

import re
import webbrowser

from typing import Union
from pathlib import Path

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QMainWindow

from gemsedit.database.connection import GemsDB
from gemsedit.utils.apputils import get_resource
from munch import Munch
# from gemsedit.pyvis.network import Network
from pyvis.network import Network
from gemsedit.database.yamlsqlexchange import load_yaml_as_dict

from gemsedit import log


def make_network(
        db: Munch, media_path: Path, directed: bool = True, layout: bool = False
) -> Network:
    net = Network(
        # height="1200px",
        bgcolor="#FFFFFF",
        directed=directed,
        layout=layout,
        notebook=False,
        width="100%",
        height="1200px",
    )

    # net.path = '/home/nogard/Dropbox/pythonProject1/pyvistemplate.html'

    # net.add_node('D', label='Delta', image=image, shape='image', title='Live Long and Prosper!')
    # net.add_edge('B', 'E', weight=.87, color='#000000')

    # add views
    for Id, view in db.Views.items():
        net.add_node(
            Id,
            label=view.Name,
            shape="image",
            # vvv direct web ref works!
            # image="http://images4.fanpop.com/image/photos/14900000/Court-Martial-mr-spock-14948576-200-200.jpg",
            # vvv local disk reference DOES NOT WORK!?
            # image=str(Path(media_path, view.Foreground)),
            image=str(Path(media_path, view.Foreground).as_uri()),
            # image="https://13thdimension.com/wp-content/uploads/2016/07/xfrtoc70fgzg49ubheth.jpg",
            title=f"View {Id}: {view.Name}",
        )

    def trigger_color(trigger: str) -> str:
        if trigger.startswith("Nav"):
            return "#66b8f9"
        elif trigger.startswith("ViewTimePassed"):
            return "#b5792a"
        else:
            return "#000000"

    # add edges
    for (
            Id,
            view,
    ) in db.Views.items():
        # check for view actions
        if view.Actions:
            for action in view.Actions.values():
                if "PortalTo" in action.Action:
                    portal_room = re.compile(r"\((\d+)\)")
                    destination = portal_room.findall(action.Action)
                    if destination:
                        net.add_edge(
                            Id,
                            destination[0],
                            weight=1.0,
                            color=trigger_color(action.Trigger),
                            title=action.Trigger,
                        )

        # check for view object actions
        if view.Objects:
            for obj in view.Objects.values():
                if obj.Actions:
                    for action in obj.Actions.values():
                        if "PortalTo" in action.Action:
                            portal_room = re.compile(r"\((\d+)\)")
                            destination = portal_room.findall(action.Action)
                            if destination:
                                if action.Trigger == "MouseClick()":
                                    trigger = f"MouseClick({obj.Id}: {obj.Name})"
                                else:
                                    trigger = action.Trigger
                                net.add_edge(
                                    Id,
                                    destination[0],
                                    weight=1.5,
                                    color=trigger_color(action.Trigger),
                                    title=trigger,
                                )

    return net


def create_network_window(url: Union[str, Path]) -> QWebEngineView:
    view = QWebEngineView()
    # view.load(QUrl(str(url)))

    html = Path(url).read_text()
    view.setHtml(html)

    return view


def show_gems_network_graph(
        parent: QMainWindow, conn: GemsDB, media_path: Union[Path, str]
):
    graph_file = str(Path(conn.tmp_folder.name, "gems_network_graph.html"))

    db = load_yaml_as_dict(conn.yaml_file_name, extra_yaml=conn.ui_list_yaml_file)
    if not db:
        log.debug(f'Unable to load database!')
        return False

    db = Munch.fromDict(db)

    network = make_network(db, media_path, directed=True, layout=False)

    network.save_graph(graph_file)
    log.debug(f'Temporarily saved network graph file to {graph_file}')

    html = Path(graph_file).read_text()

    # html = html.replace(
    #     'https://cdnjs.cloudflare.com/ajax/libs/vis/4.16.1/vis.css',
    #     f'{Path(media_path, "vis.css").as_uri()}',
    # )
    #
    # html = html.replace(
    #     'https://cdnjs.cloudflare.com/ajax/libs/vis/4.16.1/vis-network.min.js',
    #     f'{Path(media_path, "vis-network.min.js").as_uri()}',
    # )

    graph_path = Path(media_path, "env_graph.html")
    graph_path.write_text(html)
    log.debug(f'Wrote {graph_path.stat().st_size} bytes to graph file.')

    # before we show graph, we need to copy over the vis components
    try:
        js = get_resource("local_cdn", "vis-network.min.js").read_text()
        css = get_resource("local_cdn", "vis.css").read_text()
        Path(media_path, "vis.css").write_text(css)
        Path(media_path, "vis-network.min.js").write_text(js)
    except Exception as e:
        log.debug(f'Unable to copy js and css files from {str(get_resource("local_cdn"))} to {str(media_path)}: "{e}"')

    URL = Path(media_path, "env_graph.html")
    log.debug(f'URL for network graph will be {str(URL)}')

    try:
        # FIXME: Uuugghhh!! This works, but won't show the pictures, no matter
        #        how I specify the path! Until this is fixed, going back to
        #        trying to launch the graph using the default web browser.

        # _ = parent.network_window.close()
        # parent.network_window = None

        # parent.network_window = create_network_window(URL)
        # parent.network_window.show()

        # FIXME: this alternative just opens network graph html file in the default browser
        log.debug(f'about to show network graph from {str(URL.absolute().as_uri())}')
        webbrowser.open(str(URL.absolute().as_uri()), autoraise=True)
        # webbrowser.open_new(str(URL.absolute()))
    except Exception as e:
        log.warning(f'Unable to open network graph html file @ "{URL=}":\n{e}')
