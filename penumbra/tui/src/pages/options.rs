/*
    SPDX-License-Identifier: AGPL-3.0-or-later
    SPDX-FileCopyrightText: 2026 Shomy
*/
use ratatui::crossterm::event::{KeyCode, KeyEvent};
use ratatui::layout::{Alignment, Constraint, Direction, Layout, Rect};
use ratatui::prelude::*;
use ratatui::widgets::{Block, Borders, Paragraph};

use crate::app::{AppCtx, AppPage};
use crate::components::{Dropdown, DropdownOption, Stars, ThemedWidgetMut};
use crate::pages::Page;
use crate::themes::{Theme, load_themes};

pub type OptionCallback = Box<dyn Fn(&mut AppCtx, &str) + Send + Sync>;
pub type SyncCallback = Box<dyn Fn(&mut OptionWidget, &AppCtx) + Send + Sync>;

pub enum OptionWidget {
    Dropdown(Dropdown),
}

impl OptionWidget {
    pub fn render(&mut self, area: Rect, buf: &mut Buffer, theme: &Theme) {
        match self {
            OptionWidget::Dropdown(d) => d.render(area, buf, theme),
        }
    }

    pub fn render_overlay(&self, area: Rect, buf: &mut Buffer, theme: &Theme) {
        match self {
            OptionWidget::Dropdown(d) => d.render_overlay(area, buf, theme),
        }
    }
}

pub struct OptionItem {
    pub label: &'static str,
    pub description: &'static str,
    pub widget: OptionWidget,
    pub on_change: OptionCallback,
    pub sync: SyncCallback,
}

pub struct OptionSection {
    pub title: &'static str,
    pub items: Vec<OptionItem>,
}

pub struct OptionsPage {
    sections: Vec<OptionSection>,
    selected_idx: usize,
    stars: Stars,
}

impl OptionsPage {
    pub fn new() -> Self {
        let theme_registry = load_themes();

        let mut theme_options: Vec<DropdownOption> = theme_registry
            .iter()
            .map(|(id, constructor)| {
                let theme_data = constructor();
                let variant = if theme_data.is_dark { "dark" } else { "light" };

                DropdownOption {
                    label: format!("{} ({})", theme_data.name, variant),
                    value: id.to_string(),
                }
            })
            .collect();

        theme_options.sort_by(|a, b| a.label.cmp(&b.label));

        let ui_section = OptionSection {
            title: "INTERFACE",
            items: vec![OptionItem {
                label: "Antumbra Theme",
                description: "Visual style for Antumbra",
                widget: OptionWidget::Dropdown(Dropdown::new("Theme", theme_options, 0)),
                on_change: Box::new(|ctx, val| ctx.set_theme(val)),
                sync: Box::new(|w, ctx| {
                    let OptionWidget::Dropdown(d) = w;
                    d.set_by_value(ctx.theme.id);
                }),
            }],
        };

        Self { sections: vec![ui_section], selected_idx: 0, stars: Stars::new(2.0) }
    }

    fn total_items(&self) -> usize {
        self.sections.iter().map(|s| s.items.len()).sum()
    }

    fn get_item_mut(&mut self, index: usize) -> Option<&mut OptionItem> {
        let mut current = 0;
        for section in &mut self.sections {
            if index < current + section.items.len() {
                return Some(&mut section.items[index - current]);
            }
            current += section.items.len();
        }
        None
    }
}

#[async_trait::async_trait]
impl Page for OptionsPage {
    fn render(&mut self, f: &mut Frame, ctx: &mut AppCtx) {
        let area = f.area();
        self.stars.tick();
        self.stars.render(area, f.buffer_mut(), &ctx.theme);

        let main_layout = Layout::default()
            .direction(Direction::Vertical)
            .constraints([
                Constraint::Length(3),
                Constraint::Min(1),
                Constraint::Length(3),
                Constraint::Length(1),
            ])
            .margin(2)
            .split(area);

        f.render_widget(
            Paragraph::new("SETTINGS")
                .alignment(Alignment::Center)
                .style(Style::default().fg(ctx.theme.accent).add_modifier(Modifier::BOLD)),
            main_layout[0],
        );

        let list_center = Layout::default()
            .direction(Direction::Horizontal)
            .constraints([Constraint::Fill(1), Constraint::Length(60), Constraint::Fill(1)])
            .split(main_layout[1])[1];

        let mut global_idx = 0;
        let mut current_y = list_center.y;
        for section in &mut self.sections {
            let section_height = (section.items.len() as u16 * 4) + 2;
            let section_area =
                Rect::new(list_center.x, current_y, list_center.width, section_height);

            f.render_widget(
                Block::default()
                    .title(format!(" {} ", section.title))
                    .borders(Borders::ALL)
                    .border_style(Style::default().fg(ctx.theme.muted)),
                section_area,
            );
            let inner = Rect::new(
                section_area.x + 1,
                section_area.y + 1,
                section_area.width - 2,
                section_area.height - 2,
            );

            for (local_idx, opt) in section.items.iter_mut().enumerate() {
                let active = global_idx == self.selected_idx;
                let item_area =
                    Rect::new(inner.x, inner.y + (local_idx as u16 * 4), inner.width, 4);
                let chunks = Layout::default()
                    .constraints([Constraint::Length(1), Constraint::Length(3)])
                    .split(item_area);

                let label_style = if active {
                    Style::default().fg(ctx.theme.accent).add_modifier(Modifier::BOLD)
                } else {
                    Style::default().fg(ctx.theme.text)
                };
                f.render_widget(
                    Paragraph::new(Line::from(vec![
                        Span::styled(format!("{}: ", opt.label), label_style),
                        Span::styled(opt.description, Style::default().fg(ctx.theme.muted)),
                    ])),
                    chunks[0],
                );

                opt.widget.render(chunks[1], f.buffer_mut(), &ctx.theme);
                global_idx += 1;
            }
            current_y += section_height + 1;
        }

        current_y = list_center.y;
        for section in &self.sections {
            let inner_y = current_y + 1;
            for (local_idx, opt) in section.items.iter().enumerate() {
                let item_area = Rect::new(
                    list_center.x + 1,
                    inner_y + (local_idx as u16 * 4),
                    list_center.width - 2,
                    4,
                );
                let chunks = Layout::default()
                    .constraints([Constraint::Length(1), Constraint::Length(3)])
                    .split(item_area);

                opt.widget.render_overlay(chunks[1], f.buffer_mut(), &ctx.theme);
            }
            current_y += (section.items.len() as u16 * 4) + 3;
        }

        let total = self.total_items();
        let back_btn_style = if self.selected_idx == total {
            Style::default().fg(ctx.theme.accent)
        } else {
            Style::default().fg(ctx.theme.background).add_modifier(Modifier::BOLD)
        };
        f.render_widget(
            Paragraph::new(" [ Back to Menu ] ").alignment(Alignment::Center).style(back_btn_style),
            main_layout[2],
        );
        f.render_widget(
            Paragraph::new("[↑↓] Navigate   [Enter] Select   [Esc] Quick Back")
                .alignment(Alignment::Center)
                .style(Style::default().fg(ctx.theme.muted)),
            main_layout[3],
        );
    }

    async fn handle_input(&mut self, ctx: &mut AppCtx, key: KeyEvent) {
        let total = self.total_items();
        if let Some(opt) = self.get_item_mut(self.selected_idx) {
            match &mut opt.widget {
                OptionWidget::Dropdown(d) => {
                    let was_open = d.is_open();
                    if d.handle_key(key) && was_open && !d.is_open() {
                        (opt.on_change)(ctx, d.value());
                        return;
                    }
                    if d.is_open() {
                        return;
                    }
                }
            }
        }
        match key.code {
            KeyCode::Up if self.selected_idx > 0 => self.selected_idx -= 1,
            KeyCode::Down if self.selected_idx < total => self.selected_idx += 1,
            KeyCode::Enter if self.selected_idx == total => ctx.change_page(AppPage::Welcome),
            KeyCode::Esc => ctx.change_page(AppPage::Welcome),
            _ => {}
        }
    }

    async fn on_enter(&mut self, ctx: &mut AppCtx) {
        for s in &mut self.sections {
            for i in &mut s.items {
                (i.sync)(&mut i.widget, ctx);
            }
        }
    }

    async fn on_exit(&mut self, ctx: &mut AppCtx) {
        // Better save here just to be sure
        ctx.config().save().ok();
    }

    async fn update(&mut self, _: &mut AppCtx) {}
}
