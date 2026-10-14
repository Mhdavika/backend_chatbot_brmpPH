import json
from pathlib import Path


# =====================================================
# LOAD JSON
# =====================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent


FLOW_FILE = (
    BASE_DIR
    / "data"
    / "chatbot_flow.json"
)


with open(
    FLOW_FILE,
    "r",
    encoding="utf-8"
) as file:

    FLOW = json.load(file)


# =====================================================
# GET NODE
# =====================================================

def get_node(
    node_id: str
):

    if not node_id:

        return None

    return FLOW.get(
        node_id
    )


# =====================================================
# INITIAL NODE
# =====================================================

def get_initial_node():

    return FLOW.get(
        "main_menu"
    )


# =====================================================
# FIND OPTION
# =====================================================

def find_option(
    node,
    option_id: str
):

    if not node:

        return None


    option_id = str(
        option_id or ""
    ).lower().strip()


    # =================================================
    # OPTIONS
    # =================================================

    for option in node.get(
        "options",
        []
    ):

        current_id = str(
            option.get("id", "")
        ).lower().strip()


        if current_id == option_id:

            return option


    # =================================================
    # ACTIONS
    # =================================================

    for action in node.get(
        "actions",
        []
    ):

        current_id = str(
            action.get("id", "")
        ).lower().strip()


        if current_id == option_id:

            return action


    return None