---
title: db
description: DB related commands
---

# DataBase
!!! info
    **The DB CLI is almost the same as the Alembic CLI.**

# *commands*


## branches
```
ModularAPI db branches
```
*Show current branch points.*

| Option              | Description             |
|---------------------|-------------------------|
| `--verbose` or `-v` | Output in verbose mode. |

## current
```
ModularAPI db current
```
*Display the current revision for a database.*

| Option              | Description             |
|---------------------|-------------------------|
| `--verbose` or `-v` | Output in verbose mode. |

## downgrade
```
ModularAPI db downgrade <revision>
```
*Downgrade to a previous version.*

| Option  | Description       |
|---------|-------------------|
| `--sql` | Use the SQL mode. |

## edit
```
ModularAPI db edit <revision>
```
*Edit revision script(s) using $EDITOR.*

## heads
```
ModularAPI db heads
```
*Show current available heads in the script directory.*

| Option                   | Description                                 |
|--------------------------|---------------------------------------------|
| `--verbose` or `-v`      | Output in verbose mode.                     |
| `--resolve-dependencies` | Treat dependency version as down revisions. |


## history
```
ModularAPI db history
```
*List changeset scripts in chronological order.*

| Option               | Description                |
|----------------------|----------------------------|
| `--rev-range`        | String revision range.     |
| `--verbose` or `-v`  | Output in verbose mode.    |
| `--indicate-current` | Indicate current revision. |

## merge
```
ModularAPI db merge [<rev1>, <rev2>, ..., <revN>]
```
*Merge two (or more) revisions together. Creates a new migration file.*

| Option              | Description                                                    |
|---------------------|----------------------------------------------------------------|
| `--message` or `-m` | A string message to apply to the revision.                     |
| `--branch-label`    | A string label name to apply to the new revision.              |
| `--rev-id`          | Hardcoded revision identifier instead of generating a new one. |

## revision
```
ModularAPI db revision
```
*Create a new revision file.*

| Option              | Description                                                                                                                      |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------|
| `--message` or `-m` | A message to apply to the revision.                                                                                              |
| `--autogenerate`    | Whether or not to autogenerate the script from the database.                                                                     |
| `--sql`             | Whether to dump the script out as a SQL string. When specified, the script is dumped to stdout.                                  |
| `--head`            | Head revision to build the new revision upon a parent.                                                                           |
| `--splice`          | Whether or not the new revision should be made into a new head of its own, is required when the given head is not itself a head. |
| `--branche-label`   | String label to apply to the branch                                                                                              |
| `--version-path`    | String symbol identifying a specific version path from the configuration.                                                        |
| `--rev-id`          | Optional revision identifier to use instead of having one generated.                                                             |

## show
```
ModularAPI db show <rev1>
```
*Show the revision(s) denoted by the given symbol.*

## stamp
```
ModularAPI db stamp <revision="head">
```
*Stamp the revision table with the given revision; don’t run any migrations.*

| Option    | Description                                              |
|-----------|----------------------------------------------------------|
| `--sql`   | Use the SQL mode.                                        |
| `--purge` | Delete all entries in the version table before stamping. |

## upgrade
```
ModularAPI db upgrade <revision>
```
*Upgrade to a later version.*

| Option  | Description       |
|---------|-------------------|
| `--sql` | Use the SQL mode. |
