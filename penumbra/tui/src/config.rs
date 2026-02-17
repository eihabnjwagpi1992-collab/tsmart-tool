/*
    SPDX-License-Identifier: AGPL-3.0-or-later
    SPDX-FileCopyrightText: 2026 Shomy
*/

use std::fs;
use std::path::PathBuf;

use anyhow::Result;
use config::{Config, Environment, File};
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Clone, Serialize)]
pub struct AntumbraConfig {
    pub theme: String,
}

impl Default for AntumbraConfig {
    fn default() -> Self {
        Self { theme: "system".to_string() }
    }
}

impl AntumbraConfig {
    pub fn load() -> Self {
        let mut builder = Config::builder();
        let defaults = AntumbraConfig::default();

        builder = builder.set_default("theme", defaults.theme).unwrap();

        if let Some(config_dir) = dirs::config_dir().map(|p| p.join("antumbra")) {
            builder =
                builder.add_source(File::from(config_dir.join("config.toml")).required(false));
        }

        builder = builder.add_source(Environment::with_prefix("ANTUMBRA"));
        let cfg: AntumbraConfig =
            builder.build().and_then(|c| c.try_deserialize()).unwrap_or_default();

        cfg.save().ok();

        cfg
    }

    pub fn save(&self) -> Result<()> {
        if let Some(path) = Self::get_path() {
            if let Some(parent) = path.parent() {
                fs::create_dir_all(parent)?;
            }

            let toml_string = toml::to_string_pretty(self)?;
            fs::write(path, toml_string)?;
        }
        Ok(())
    }

    fn get_path() -> Option<PathBuf> {
        dirs::config_dir().map(|p| p.join("antumbra/config.toml"))
    }
}
