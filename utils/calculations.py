def calculate_progress(target, achievement, uom):
    if target == 0:
        return 0

    if uom == "Numeric":
        return round((achievement / target) * 100, 2)

    elif uom == "Percentage":
        return round((achievement / target) * 100, 2)

    elif uom == "Zero":
        return 100 if achievement == 0 else 0

    else:
        return 0