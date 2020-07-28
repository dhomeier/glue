import os

from qtpy import QtWidgets

from echo.qt import autoconnect_callbacks_to_qt
from glue.utils.qt import load_ui, fix_tab_widget_fontsize
from glue.viewers.matplotlib.state import MatplotlibDataViewerState

__all__ = ['ScatterOptionsWidget']


def _get_labels(proj):
    if proj == 'rectilinear':
        return 'x_axis', 'y_axis'
    elif proj == 'polar':
        return 'theta (rad)', 'radius'
    elif proj in ['aitoff', 'hammer', 'lambert', 'mollweide']:
        return 'longitude (rad)', 'latitude (rad)'
    else:
        return 'axis 1', 'axis 2'

class ScatterOptionsWidget(QtWidgets.QWidget):

    def __init__(self, viewer_state, session, parent=None):

        super(ScatterOptionsWidget, self).__init__(parent=parent)

        self.ui = load_ui('options_widget.ui', self,
                          directory=os.path.dirname(__file__))

        fix_tab_widget_fontsize(self.ui.tab_widget)

        self._connections = autoconnect_callbacks_to_qt(viewer_state, self.ui)
        self._connections_axes = autoconnect_callbacks_to_qt(viewer_state, self.ui.axes_editor.ui)
        connect_kwargs = {'alpha': dict(value_range=(0, 1))}
        self._connections_legend = autoconnect_callbacks_to_qt(viewer_state.legend, self.ui.legend_editor.ui, connect_kwargs)

        self.viewer_state = viewer_state

        viewer_state.add_callback('x_att', self._update_x_attribute)
        viewer_state.add_callback('y_att', self._update_y_attribute)
        viewer_state.add_callback('plot_mode', self._update_plot_mode)

        self.session = session
        self.ui.axes_editor.button_apply_all.clicked.connect(self._apply_all_viewers)

    def _apply_all_viewers(self):
        for tab in self.session.application.viewers:
            for viewer in tab:
                if isinstance(viewer.state, MatplotlibDataViewerState):
                    viewer.state.update_axes_settings_from(self.viewer_state)

    def _update_x_attribute(self, *args):
        # If at least one of the components is categorical or a date, disable log button
        log_enabled = 'categorical' not in self.viewer_state.x_kinds
        self.ui.bool_x_log.setEnabled(log_enabled)
        self.ui.bool_x_log_.setEnabled(log_enabled)
        if not log_enabled:
            self.ui.bool_x_log.setChecked(False)
            self.ui.bool_x_log_.setChecked(False)

    def _update_y_attribute(self, *args):
        # If at least one of the components is categorical or a date, disable log button
        log_enabled = 'categorical' not in self.viewer_state.y_kinds
        self.ui.bool_y_log.setEnabled(log_enabled)
        self.ui.bool_y_log_.setEnabled(log_enabled)
        if not log_enabled:
            self.ui.bool_y_log.setChecked(False)
            self.ui.bool_y_log_.setChecked(False)

    def _update_plot_mode(self, *args):
        x_label, y_label = _get_labels(self.viewer_state.plot_mode)
        self.ui.x_lab.setText(x_label)
        self.ui.x_lab_2.setText(x_label)
        self.ui.y_lab.setText(y_label)
        self.ui.y_lab_2.setText(y_label)
