/*
    SPDX-License-Identifier: AGPL-3.0-or-later
    SPDX-FileCopyrightText: 2026 Shomy
*/
use ratatui::buffer::Buffer;
use ratatui::crossterm::event::{KeyCode, KeyEvent};
use ratatui::layout::{Constraint, Direction, Layout, Rect};
use ratatui::style::{Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Clear, Paragraph, Widget};

use crate::components::ThemedWidgetMut;
use crate::themes::Theme;

#[derive(Clone)]
pub struct DropdownOption {
    pub label: String,
    pub value: String,
}

pub struct Dropdown {
    label: String,
    options: Vec<DropdownOption>,
    selected: usize,
    open: bool,
}

impl Dropdown {
    pub fn new(label: impl Into<String>, options: Vec<DropdownOption>, selected: usize) -> Self {
        Self { label: label.into(), options, selected, open: false }
    }

    /// Returns the internal value of the selected option
    pub fn value(&self) -> &String {
        &self.options[self.selected].value
    }

    /// Returns the display label of the selected option
    pub fn selected_label(&self) -> &String {
        &self.options[self.selected].label
    }

    pub fn is_open(&self) -> bool {
        self.open
    }

    #[allow(dead_code)]
    pub fn set_selected(&mut self, idx: usize) {
        if idx < self.options.len() {
            self.selected = idx;
        }
    }

    pub fn set_by_value(&mut self, value: &str) {
        if let Some(index) = self.options.iter().position(|opt| opt.value == value) {
            self.selected = index;
        }
    }

    pub fn handle_key(&mut self, key: KeyEvent) -> bool {
        match key.code {
            KeyCode::Enter => {
                self.open = !self.open;
                true
            }
            KeyCode::Up if self.open => {
                if self.selected > 0 {
                    self.selected -= 1;
                }
                true
            }
            KeyCode::Down if self.open => {
                if self.selected + 1 < self.options.len() {
                    self.selected += 1;
                }
                true
            }
            KeyCode::Esc if self.open => {
                self.open = false;
                true
            }
            _ => false,
        }
    }
}

impl ThemedWidgetMut for Dropdown {
    fn render(&mut self, area: Rect, buf: &mut Buffer, theme: &Theme) {
        let layout = Layout::default()
            .direction(Direction::Horizontal)
            .constraints([Constraint::Length(20), Constraint::Min(10)])
            .split(area);

        buf.set_string(
            layout[0].x,
            layout[0].y + 1,
            &self.label,
            Style::default().fg(theme.text).add_modifier(Modifier::BOLD),
        );

        let symbol = if self.open { "▲" } else { "▼" };
        let text = format!(
            " {:<width$} {} ",
            self.selected_label(),
            symbol,
            width = layout[1].width.saturating_sub(6) as usize
        );

        let border_style = if self.open {
            Style::default().fg(theme.accent)
        } else {
            Style::default().fg(theme.muted)
        };

        Paragraph::new(text)
            .style(Style::default().fg(theme.text).bg(theme.background))
            .block(Block::default().borders(Borders::ALL).border_style(border_style))
            .render(layout[1], buf);
    }

    fn render_overlay(&self, area: Rect, buf: &mut Buffer, theme: &Theme) {
        if !self.open {
            return;
        }

        let box_area = Layout::default()
            .direction(Direction::Horizontal)
            .constraints([Constraint::Length(20), Constraint::Min(10)])
            .split(area)[1];

        let list_height = (self.options.len() as u16).min(10);
        let list_area = Rect {
            x: box_area.x,
            y: box_area.y + box_area.height,
            width: box_area.width,
            height: list_height + 2,
        };

        Clear.render(list_area, buf);

        let lines: Vec<Line> = self
            .options
            .iter()
            .enumerate()
            .map(|(i, opt)| {
                let mut style = Style::default().fg(theme.text).bg(theme.background);
                if i == self.selected {
                    style = style.bg(theme.highlight).add_modifier(Modifier::BOLD);
                }
                Line::from(Span::styled(format!("  {}", opt.label), style))
            })
            .collect();

        Paragraph::new(lines)
            .block(
                Block::default()
                    .borders(Borders::ALL)
                    .border_style(Style::default().fg(theme.accent)),
            )
            .render(list_area, buf);
    }
}
