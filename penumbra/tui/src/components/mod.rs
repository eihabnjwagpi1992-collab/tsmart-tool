pub mod blinking_stars;
pub mod card_view;
pub mod description_menu;
pub mod dialog;
pub mod dropdown;
pub mod file_explorer;
pub mod progress_bar;
pub mod selectable_list;
// Re-exports :D

pub use blinking_stars::Stars;
pub use card_view::{Card, CardRow};
pub use description_menu::{DescriptionMenu, DescriptionMenuItem};
pub use dialog::{DialogBuilder, DialogButton};
pub use dropdown::{Dropdown, DropdownOption};
pub use file_explorer::{ExplorerResult, FileExplorer};
pub use progress_bar::ProgressBar;
use ratatui::buffer::Buffer;
use ratatui::layout::Rect;

use crate::themes::Theme;

/// A widget that also accepts a theme for rendering.
pub trait ThemedWidget {
    fn render(self, area: Rect, buf: &mut Buffer, theme: &Theme)
    where
        Self: Sized;

    fn render_overlay(self, _area: Rect, _buf: &mut Buffer, _theme: &Theme)
    where
        Self: Sized,
    {
    }
}

pub trait ThemedWidgetRef {
    fn render_ref(&self, area: Rect, buf: &mut Buffer, theme: &Theme);
}

pub trait StatefulThemedWidget {
    type State;
    fn render(&mut self, area: Rect, buf: &mut Buffer, state: &mut Self::State, theme: &Theme);
}

pub trait ThemedWidgetMut {
    fn render(&mut self, area: Rect, buf: &mut Buffer, theme: &Theme);
    fn render_overlay(&self, _area: Rect, _buf: &mut Buffer, _theme: &Theme) {}
}
