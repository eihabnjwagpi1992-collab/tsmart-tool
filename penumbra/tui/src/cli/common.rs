/*
    SPDX-License-Identifier: AGPL-3.0-or-later
    SPDX-FileCopyrightText: 2025 Shomy
*/
use std::path::PathBuf;

#[allow(dead_code)]
pub const CONN_BR: u8 = 0;
#[allow(dead_code)]
pub const CONN_PL: u8 = 1;
pub const CONN_DA: u8 = 2;

use clap::Args;

#[derive(Args, Debug)]
pub struct DaArgs {
    // The DA file to use
    #[arg(short, long = "da", value_name = "DA_FILE")]
    pub da_file: PathBuf,
    // #[arg(long, value_name = "AUTH_FILE")]
    // pub auth_file: Option<PathBuf>,
    // The preloader file to use
    #[arg(short, long = "pl", value_name = "PRELOADER_FILE")]
    pub preloader_file: Option<PathBuf>,
}

/// A trait for providing metadata for CLI commands.
/// This trait can be implemented by command structs to give additional info
pub trait CommandMetadata {
    fn aliases() -> &'static [&'static str] {
        &[]
    }
    fn visible_aliases() -> &'static [&'static str] {
        &[]
    }
    fn about() -> &'static str {
        ""
    }
    fn long_about() -> &'static str {
        ""
    }
    fn hide() -> bool {
        false
    }
}
