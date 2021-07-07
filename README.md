Needed environment variables:

* FLASK_APP (geocoding_cache/server.py)
* GOOGLE_API_KEY
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* DATABASE_URL (path to a sqlite3 database)

Database setup and migrations are handled by [`diesel_cli`](https://github.com/diesel-rs/diesel/tree/master/diesel_cli).
To set up a fresh (empty) database:

* Install rustup/rust (https://rustup.rs/)
* Install `diesel_cli` with:
    
   `cargo install diesel_cli --no-default-features --features "sqlite"`
* Run `diesel database setup`
