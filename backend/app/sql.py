def season_clause(alias: str = "g") -> str:
    return f" AND ({alias}.season = %(season)s OR %(season)s IN ('All', 'All seasons', '所有賽季'))"


def game_type_clause(alias: str = "g") -> str:
    return (
        f" AND ({alias}.game_type = %(game_type)s "
        f"OR %(game_type)s IN ('All', 'All games', '全部賽事', '所有賽事'))"
    )


def postseason_stage_clause(alias: str = "g") -> str:
    return (
        f" AND ({alias}.postseason_stage = %(postseason_stage)s "
        f"OR %(postseason_stage)s IN ('All', 'All stages', '全部階段', '所有階段'))"
    )
