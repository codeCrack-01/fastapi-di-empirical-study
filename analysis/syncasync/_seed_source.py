"""Vendored schema and seed data for the read-only benchmark database.

Generated from analysis/experiment/core/db.py so the study box (which receives
only analysis/syncasync) can rebuild the database byte-identically without the
archived experiment tree. Do not hand-edit: regenerate with
tools/vendor_seed.py.
"""

SCHEMA = "\nCREATE TABLE IF NOT EXISTS users (\n    id INTEGER PRIMARY KEY,\n    username TEXT UNIQUE NOT NULL,\n    email TEXT NOT NULL,\n    role TEXT NOT NULL,               -- admin | editor | user\n    auth_token TEXT UNIQUE NOT NULL,\n    suspended INTEGER NOT NULL DEFAULT 0\n);\nCREATE TABLE IF NOT EXISTS reviews (\n    id INTEGER PRIMARY KEY,\n    title TEXT NOT NULL,\n    body TEXT NOT NULL,\n    author TEXT NOT NULL,\n    status TEXT NOT NULL,             -- pending | approved | flagged | deleted\n    rating INTEGER NOT NULL,\n    votes INTEGER NOT NULL DEFAULT 0\n);\nCREATE TABLE IF NOT EXISTS comments (\n    id INTEGER PRIMARY KEY,\n    review_id INTEGER NOT NULL,\n    author TEXT NOT NULL,\n    body TEXT NOT NULL\n);\nCREATE TABLE IF NOT EXISTS audit (\n    id INTEGER PRIMARY KEY,\n    actor TEXT NOT NULL,\n    action TEXT NOT NULL\n);\nCREATE TABLE IF NOT EXISTS config (\n    key TEXT PRIMARY KEY,\n    value TEXT NOT NULL\n);\n"

SEED_ROWS = {
    "users": [
        {
            "id": 1,
            "username": "alice",
            "email": "alice@example.com",
            "role": "admin",
            "auth_token": "admin-token",
            "suspended": 0
        },
        {
            "id": 2,
            "username": "bob",
            "email": "bob@example.com",
            "role": "admin",
            "auth_token": "bob-token",
            "suspended": 0
        },
        {
            "id": 3,
            "username": "carol",
            "email": "carol@example.com",
            "role": "admin",
            "auth_token": "carol-token",
            "suspended": 0
        },
        {
            "id": 4,
            "username": "dave",
            "email": "dave@example.com",
            "role": "editor",
            "auth_token": "editor-token",
            "suspended": 0
        },
        {
            "id": 5,
            "username": "erin",
            "email": "erin@example.com",
            "role": "editor",
            "auth_token": "erin-token",
            "suspended": 0
        },
        {
            "id": 6,
            "username": "frank",
            "email": "frank@example.com",
            "role": "user",
            "auth_token": "user-token",
            "suspended": 0
        },
        {
            "id": 7,
            "username": "grace",
            "email": "grace@example.com",
            "role": "user",
            "auth_token": "grace-token",
            "suspended": 0
        },
        {
            "id": 8,
            "username": "heidi",
            "email": "heidi@example.com",
            "role": "user",
            "auth_token": "heidi-token",
            "suspended": 0
        },
        {
            "id": 9,
            "username": "ivan",
            "email": "ivan@example.com",
            "role": "user",
            "auth_token": "ivan-token",
            "suspended": 0
        }
    ],
    "reviews": [
        {
            "id": 1,
            "title": "Review 1",
            "body": "Body of review 1",
            "author": "frank",
            "status": "approved",
            "rating": 2,
            "votes": 1
        },
        {
            "id": 2,
            "title": "Review 2",
            "body": "Body of review 2",
            "author": "frank",
            "status": "approved",
            "rating": 3,
            "votes": 2
        },
        {
            "id": 3,
            "title": "Review 3",
            "body": "Body of review 3",
            "author": "alice",
            "status": "approved",
            "rating": 4,
            "votes": 3
        },
        {
            "id": 4,
            "title": "Review 4",
            "body": "Body of review 4",
            "author": "frank",
            "status": "approved",
            "rating": 5,
            "votes": 4
        },
        {
            "id": 5,
            "title": "Review 5",
            "body": "Body of review 5",
            "author": "frank",
            "status": "pending",
            "rating": 1,
            "votes": 5
        },
        {
            "id": 6,
            "title": "Review 6",
            "body": "Body of review 6",
            "author": "alice",
            "status": "approved",
            "rating": 2,
            "votes": 6
        },
        {
            "id": 7,
            "title": "Review 7",
            "body": "Body of review 7",
            "author": "frank",
            "status": "approved",
            "rating": 3,
            "votes": 0
        },
        {
            "id": 8,
            "title": "Review 8",
            "body": "Body of review 8",
            "author": "frank",
            "status": "approved",
            "rating": 4,
            "votes": 1
        },
        {
            "id": 9,
            "title": "Review 9",
            "body": "Body of review 9",
            "author": "alice",
            "status": "approved",
            "rating": 5,
            "votes": 2
        },
        {
            "id": 10,
            "title": "Review 10",
            "body": "Body of review 10",
            "author": "frank",
            "status": "pending",
            "rating": 1,
            "votes": 3
        },
        {
            "id": 11,
            "title": "Review 11",
            "body": "Body of review 11",
            "author": "frank",
            "status": "approved",
            "rating": 2,
            "votes": 4
        },
        {
            "id": 12,
            "title": "Review 12",
            "body": "Body of review 12",
            "author": "alice",
            "status": "approved",
            "rating": 3,
            "votes": 5
        },
        {
            "id": 13,
            "title": "Review 13",
            "body": "Body of review 13",
            "author": "frank",
            "status": "approved",
            "rating": 4,
            "votes": 6
        },
        {
            "id": 14,
            "title": "Review 14",
            "body": "Body of review 14",
            "author": "frank",
            "status": "approved",
            "rating": 5,
            "votes": 0
        },
        {
            "id": 15,
            "title": "Review 15",
            "body": "Body of review 15",
            "author": "alice",
            "status": "pending",
            "rating": 1,
            "votes": 1
        },
        {
            "id": 16,
            "title": "Review 16",
            "body": "Body of review 16",
            "author": "frank",
            "status": "approved",
            "rating": 2,
            "votes": 2
        },
        {
            "id": 17,
            "title": "Review 17",
            "body": "Body of review 17",
            "author": "frank",
            "status": "approved",
            "rating": 3,
            "votes": 3
        },
        {
            "id": 18,
            "title": "Review 18",
            "body": "Body of review 18",
            "author": "alice",
            "status": "approved",
            "rating": 4,
            "votes": 4
        },
        {
            "id": 19,
            "title": "Review 19",
            "body": "Body of review 19",
            "author": "frank",
            "status": "approved",
            "rating": 5,
            "votes": 5
        },
        {
            "id": 20,
            "title": "Review 20",
            "body": "Body of review 20",
            "author": "frank",
            "status": "pending",
            "rating": 1,
            "votes": 6
        },
        {
            "id": 21,
            "title": "Review 21",
            "body": "Body of review 21",
            "author": "alice",
            "status": "approved",
            "rating": 2,
            "votes": 0
        },
        {
            "id": 22,
            "title": "Review 22",
            "body": "Body of review 22",
            "author": "frank",
            "status": "approved",
            "rating": 3,
            "votes": 1
        },
        {
            "id": 23,
            "title": "Review 23",
            "body": "Body of review 23",
            "author": "frank",
            "status": "approved",
            "rating": 4,
            "votes": 2
        },
        {
            "id": 24,
            "title": "Review 24",
            "body": "Body of review 24",
            "author": "alice",
            "status": "approved",
            "rating": 5,
            "votes": 3
        },
        {
            "id": 25,
            "title": "Review 25",
            "body": "Body of review 25",
            "author": "frank",
            "status": "pending",
            "rating": 1,
            "votes": 4
        },
        {
            "id": 26,
            "title": "Review 26",
            "body": "Body of review 26",
            "author": "frank",
            "status": "approved",
            "rating": 2,
            "votes": 5
        },
        {
            "id": 27,
            "title": "Review 27",
            "body": "Body of review 27",
            "author": "alice",
            "status": "approved",
            "rating": 3,
            "votes": 6
        },
        {
            "id": 28,
            "title": "Review 28",
            "body": "Body of review 28",
            "author": "frank",
            "status": "approved",
            "rating": 4,
            "votes": 0
        },
        {
            "id": 29,
            "title": "Review 29",
            "body": "Body of review 29",
            "author": "frank",
            "status": "approved",
            "rating": 5,
            "votes": 1
        },
        {
            "id": 30,
            "title": "Review 30",
            "body": "Body of review 30",
            "author": "alice",
            "status": "pending",
            "rating": 1,
            "votes": 2
        },
        {
            "id": 31,
            "title": "Review 31",
            "body": "Body of review 31",
            "author": "frank",
            "status": "approved",
            "rating": 2,
            "votes": 3
        },
        {
            "id": 32,
            "title": "Review 32",
            "body": "Body of review 32",
            "author": "frank",
            "status": "approved",
            "rating": 3,
            "votes": 4
        },
        {
            "id": 33,
            "title": "Review 33",
            "body": "Body of review 33",
            "author": "alice",
            "status": "approved",
            "rating": 4,
            "votes": 5
        },
        {
            "id": 34,
            "title": "Review 34",
            "body": "Body of review 34",
            "author": "frank",
            "status": "approved",
            "rating": 5,
            "votes": 6
        },
        {
            "id": 35,
            "title": "Review 35",
            "body": "Body of review 35",
            "author": "frank",
            "status": "pending",
            "rating": 1,
            "votes": 0
        },
        {
            "id": 36,
            "title": "Review 36",
            "body": "Body of review 36",
            "author": "alice",
            "status": "approved",
            "rating": 2,
            "votes": 1
        },
        {
            "id": 37,
            "title": "Review 37",
            "body": "Body of review 37",
            "author": "frank",
            "status": "approved",
            "rating": 3,
            "votes": 2
        },
        {
            "id": 38,
            "title": "Review 38",
            "body": "Body of review 38",
            "author": "frank",
            "status": "approved",
            "rating": 4,
            "votes": 3
        },
        {
            "id": 39,
            "title": "Review 39",
            "body": "Body of review 39",
            "author": "alice",
            "status": "approved",
            "rating": 5,
            "votes": 4
        },
        {
            "id": 40,
            "title": "Review 40",
            "body": "Body of review 40",
            "author": "frank",
            "status": "pending",
            "rating": 1,
            "votes": 5
        }
    ],
    "comments": [
        {
            "id": 1,
            "review_id": 2,
            "author": "grace",
            "body": "Comment 1"
        },
        {
            "id": 2,
            "review_id": 3,
            "author": "grace",
            "body": "Comment 2"
        },
        {
            "id": 3,
            "review_id": 4,
            "author": "grace",
            "body": "Comment 3"
        },
        {
            "id": 4,
            "review_id": 5,
            "author": "grace",
            "body": "Comment 4"
        },
        {
            "id": 5,
            "review_id": 6,
            "author": "grace",
            "body": "Comment 5"
        },
        {
            "id": 6,
            "review_id": 7,
            "author": "grace",
            "body": "Comment 6"
        },
        {
            "id": 7,
            "review_id": 8,
            "author": "grace",
            "body": "Comment 7"
        },
        {
            "id": 8,
            "review_id": 9,
            "author": "grace",
            "body": "Comment 8"
        },
        {
            "id": 9,
            "review_id": 10,
            "author": "grace",
            "body": "Comment 9"
        },
        {
            "id": 10,
            "review_id": 11,
            "author": "grace",
            "body": "Comment 10"
        },
        {
            "id": 11,
            "review_id": 12,
            "author": "grace",
            "body": "Comment 11"
        },
        {
            "id": 12,
            "review_id": 13,
            "author": "grace",
            "body": "Comment 12"
        },
        {
            "id": 13,
            "review_id": 14,
            "author": "grace",
            "body": "Comment 13"
        },
        {
            "id": 14,
            "review_id": 15,
            "author": "grace",
            "body": "Comment 14"
        },
        {
            "id": 15,
            "review_id": 16,
            "author": "grace",
            "body": "Comment 15"
        },
        {
            "id": 16,
            "review_id": 17,
            "author": "grace",
            "body": "Comment 16"
        },
        {
            "id": 17,
            "review_id": 18,
            "author": "grace",
            "body": "Comment 17"
        },
        {
            "id": 18,
            "review_id": 19,
            "author": "grace",
            "body": "Comment 18"
        },
        {
            "id": 19,
            "review_id": 20,
            "author": "grace",
            "body": "Comment 19"
        },
        {
            "id": 20,
            "review_id": 21,
            "author": "grace",
            "body": "Comment 20"
        },
        {
            "id": 21,
            "review_id": 22,
            "author": "grace",
            "body": "Comment 21"
        },
        {
            "id": 22,
            "review_id": 23,
            "author": "grace",
            "body": "Comment 22"
        },
        {
            "id": 23,
            "review_id": 24,
            "author": "grace",
            "body": "Comment 23"
        },
        {
            "id": 24,
            "review_id": 25,
            "author": "grace",
            "body": "Comment 24"
        },
        {
            "id": 25,
            "review_id": 26,
            "author": "grace",
            "body": "Comment 25"
        },
        {
            "id": 26,
            "review_id": 27,
            "author": "grace",
            "body": "Comment 26"
        },
        {
            "id": 27,
            "review_id": 28,
            "author": "grace",
            "body": "Comment 27"
        },
        {
            "id": 28,
            "review_id": 29,
            "author": "grace",
            "body": "Comment 28"
        },
        {
            "id": 29,
            "review_id": 30,
            "author": "grace",
            "body": "Comment 29"
        },
        {
            "id": 30,
            "review_id": 31,
            "author": "grace",
            "body": "Comment 30"
        },
        {
            "id": 31,
            "review_id": 32,
            "author": "grace",
            "body": "Comment 31"
        },
        {
            "id": 32,
            "review_id": 33,
            "author": "grace",
            "body": "Comment 32"
        },
        {
            "id": 33,
            "review_id": 34,
            "author": "grace",
            "body": "Comment 33"
        },
        {
            "id": 34,
            "review_id": 35,
            "author": "grace",
            "body": "Comment 34"
        },
        {
            "id": 35,
            "review_id": 36,
            "author": "grace",
            "body": "Comment 35"
        },
        {
            "id": 36,
            "review_id": 37,
            "author": "grace",
            "body": "Comment 36"
        },
        {
            "id": 37,
            "review_id": 38,
            "author": "grace",
            "body": "Comment 37"
        },
        {
            "id": 38,
            "review_id": 39,
            "author": "grace",
            "body": "Comment 38"
        },
        {
            "id": 39,
            "review_id": 40,
            "author": "grace",
            "body": "Comment 39"
        },
        {
            "id": 40,
            "review_id": 1,
            "author": "grace",
            "body": "Comment 40"
        },
        {
            "id": 41,
            "review_id": 2,
            "author": "grace",
            "body": "Comment 41"
        },
        {
            "id": 42,
            "review_id": 3,
            "author": "grace",
            "body": "Comment 42"
        },
        {
            "id": 43,
            "review_id": 4,
            "author": "grace",
            "body": "Comment 43"
        },
        {
            "id": 44,
            "review_id": 5,
            "author": "grace",
            "body": "Comment 44"
        },
        {
            "id": 45,
            "review_id": 6,
            "author": "grace",
            "body": "Comment 45"
        },
        {
            "id": 46,
            "review_id": 7,
            "author": "grace",
            "body": "Comment 46"
        },
        {
            "id": 47,
            "review_id": 8,
            "author": "grace",
            "body": "Comment 47"
        },
        {
            "id": 48,
            "review_id": 9,
            "author": "grace",
            "body": "Comment 48"
        },
        {
            "id": 49,
            "review_id": 10,
            "author": "grace",
            "body": "Comment 49"
        },
        {
            "id": 50,
            "review_id": 11,
            "author": "grace",
            "body": "Comment 50"
        },
        {
            "id": 51,
            "review_id": 12,
            "author": "grace",
            "body": "Comment 51"
        },
        {
            "id": 52,
            "review_id": 13,
            "author": "grace",
            "body": "Comment 52"
        },
        {
            "id": 53,
            "review_id": 14,
            "author": "grace",
            "body": "Comment 53"
        },
        {
            "id": 54,
            "review_id": 15,
            "author": "grace",
            "body": "Comment 54"
        },
        {
            "id": 55,
            "review_id": 16,
            "author": "grace",
            "body": "Comment 55"
        },
        {
            "id": 56,
            "review_id": 17,
            "author": "grace",
            "body": "Comment 56"
        },
        {
            "id": 57,
            "review_id": 18,
            "author": "grace",
            "body": "Comment 57"
        },
        {
            "id": 58,
            "review_id": 19,
            "author": "grace",
            "body": "Comment 58"
        },
        {
            "id": 59,
            "review_id": 20,
            "author": "grace",
            "body": "Comment 59"
        },
        {
            "id": 60,
            "review_id": 21,
            "author": "grace",
            "body": "Comment 60"
        }
    ],
    "audit": [],
    "config": [
        {
            "key": "max_editors",
            "value": "8"
        },
        {
            "key": "backup_interval_h",
            "value": "24"
        },
        {
            "key": "audit_enabled",
            "value": "true"
        }
    ]
}
