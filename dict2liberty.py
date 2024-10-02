def dict2liberty(liberty, current_group=None, indent=2):
  """Convert a dictionary to a Liberty library"""
  # If current_group is None, then this is the top-level group, take library
  if current_group is None:
    liberty, current_group = liberty["library"], "library"

  # Retrieve attributes and groups
  def isgroup(x):
    return isinstance(x, (dict, list))
  attributes = {k : v for k, v in liberty.items() if not isgroup(v) and k != "comment"}
  groupss = {k : v if isinstance(v, list) else [v] for k, v in liberty.items() if isgroup(v)}

  # Initialize liberty
  liberty = []

  # Attributes
  for k, v in attributes.items():
    if isinstance(v, tuple):
      text = f'{k} ('
      if isinstance(v[0], Iterable):
        text += " \\\n"
        text += ", \\\n".join([" "* indent + f'"{str(l)[1:-1].strip(",")}"' for l in v])
        text += " \\\n"
      elif isinstance(v[0], (int, float)):
        text += f'"{str(v)[1:-1].strip(",")}"'
      text += ");"
      liberty.append(text)
    elif k == "capacitive_load_unit":
      liberty.append(f"{k} ({v});")
    elif isinstance(v, str):
      liberty.append(f'{k} : "{v}";')
    else:
      liberty.append(f"{k} : {str(v).lower()};")

  # Groups (special groups have no name, e.g., "timing () {")
  special_groups = ["timing", "memory", "memory_read", "memory_write", "internal_power"]
  for group_name, groups in groupss.items():
    for group in groups:
      # Debug show cell
      if debug and current_group == "cell":
        dbg_logger.info(f"DEBUG: Exporting cell {group_name}")

      # Group name header
      if not attributes:
        liberty.append(f"{current_group} ({group_name}) " + "{")
      elif group_name in special_groups:
        liberty.append(f"{group_name} () " + "{")

      # Add group name
      grouplib = dict2liberty(group, group_name, indent, debug, dbg_logger)

      # Indent
      if not attributes or group_name in special_groups:
        grouplib = [" "*indent + line for line in grouplib.split("\n")]
      else:
        grouplib = grouplib.split("\n")

      # Insert
      liberty.extend(grouplib)

      # Add closing brace
      if not attributes or group_name in special_groups:
        liberty.append("}")

  # Return final Liberty
  return "\n".join(liberty)
