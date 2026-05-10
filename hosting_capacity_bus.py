"""Educational Manim scene about bus hosting capacity in power systems.

The scene explains, in Portuguese, that the hosting capacity of a bus is the
largest distributed generation power that can be connected while respecting
voltage, thermal current, and reverse-power-flow operating limits.
"""

from manim import *


NETWORK_BLUE = BLUE_C
PV_ORANGE = ORANGE
PV_YELLOW = YELLOW
VIOLATION_RED = RED_C
ACCEPTABLE_GREEN = GREEN_C
AUX_GRAY = GRAY_B
DARK_TEXT = WHITE

P_MAX = 250
V_LIMIT_LOW = 0.95
V_LIMIT_HIGH = 1.05
P_HC_V = 180
P_HC_I = 230
P_HC_R = 210
HC_FINAL = 180
V_SLOPE = 0.00028
P_LOCAL_LOAD = 80
P_REVERSE_LIMIT = P_HC_R - P_LOCAL_LOAD


def voltage_from_power(power_kw):
    """Return the didactic bus voltage for a given distributed generation power."""
    return 1.00 + V_SLOPE * power_kw


def current_loading_from_power(power_kw):
    """Return a didactic feeder current loading ratio."""
    return 0.35 + 0.65 * power_kw / P_HC_I


def reverse_power_from_generation(power_kw):
    """Return a didactic reverse power flow value in kW."""
    return max(0, power_kw - P_LOCAL_LOAD)


def make_power_arrow(start, end, label, color=NETWORK_BLUE):
    """Create an arrow with a compact label."""
    arrow = Arrow(start, end, buff=0.12, color=color, stroke_width=6, max_tip_length_to_length_ratio=0.12)
    text = Text(label, font_size=24, color=color)
    text.next_to(arrow, UP, buff=0.12)
    return VGroup(arrow, text)


def make_network_diagram(scale=1.0, show_status=False, overloaded=False):
    """Build the simplified radial feeder diagram."""
    sub = VGroup(
        Rectangle(width=0.75, height=1.2, color=NETWORK_BLUE, stroke_width=3),
        Line(LEFT * 0.28 + UP * 0.35, RIGHT * 0.28 + UP * 0.35, color=NETWORK_BLUE),
        Line(LEFT * 0.28, RIGHT * 0.28, color=NETWORK_BLUE),
        Line(LEFT * 0.28 + DOWN * 0.35, RIGHT * 0.28 + DOWN * 0.35, color=NETWORK_BLUE),
    )
    sub.move_to(LEFT * 4.8 + UP * 0.25)
    sub_label = Text("Subestação", font_size=24, color=DARK_TEXT).next_to(sub, DOWN, buff=0.18)

    bus_color = VIOLATION_RED if overloaded else NETWORK_BLUE
    bus = Line(DOWN * 1.0, UP * 1.0, color=bus_color, stroke_width=9).move_to(RIGHT * 1.0 + UP * 0.25)
    bus_label = Text("Barra k", font_size=30, color=bus_color).next_to(bus, UP, buff=0.16)

    feeder = Line(sub.get_right(), bus.get_left(), color=NETWORK_BLUE, stroke_width=6)
    feeder_label = Text("Alimentador", font_size=24, color=DARK_TEXT).next_to(feeder, UP, buff=0.18)

    load = VGroup(
        Polygon(LEFT * 0.45 + UP * 0.35, RIGHT * 0.45 + UP * 0.35, ORIGIN + DOWN * 0.45, color=AUX_GRAY),
        Line(ORIGIN + UP * 0.35, ORIGIN + UP * 0.85, color=AUX_GRAY),
    )
    load.move_to(RIGHT * 3.7 + DOWN * 1.2)
    load_line = Line(bus.get_bottom(), load[1].get_top(), color=AUX_GRAY, stroke_width=4)
    load_label = Text("Carga", font_size=24, color=DARK_TEXT).next_to(load, DOWN, buff=0.16)

    pv_panel = VGroup()
    panel = Rectangle(width=1.05, height=0.7, color=PV_ORANGE, fill_color=PV_YELLOW, fill_opacity=0.35, stroke_width=3)
    grid_lines = VGroup(
        Line(panel.get_left(), panel.get_right(), color=PV_ORANGE, stroke_width=1.5).shift(UP * 0.12),
        Line(panel.get_left(), panel.get_right(), color=PV_ORANGE, stroke_width=1.5).shift(DOWN * 0.12),
        Line(panel.get_top(), panel.get_bottom(), color=PV_ORANGE, stroke_width=1.5).shift(LEFT * 0.18),
        Line(panel.get_top(), panel.get_bottom(), color=PV_ORANGE, stroke_width=1.5).shift(RIGHT * 0.18),
    )
    sun = VGroup(
        Circle(radius=0.18, color=PV_YELLOW, fill_color=PV_YELLOW, fill_opacity=0.85),
        *[Line(ORIGIN, UP * 0.18, color=PV_YELLOW, stroke_width=2).rotate(a).shift(UP * 0.5) for a in [0, PI / 4, PI / 2, 3 * PI / 4, PI, 5 * PI / 4, 3 * PI / 2, 7 * PI / 4]],
    )
    sun.next_to(panel, UP, buff=0.12)
    pv_panel.add(panel, grid_lines, sun)
    pv_panel.move_to(RIGHT * 3.7 + UP * 1.35)
    pv_line = Line(pv_panel.get_left(), bus.get_right(), color=PV_ORANGE, stroke_width=4)
    pv_label = Text("GD Fotovoltaica", font_size=24, color=PV_ORANGE).next_to(pv_panel, UP, buff=0.35)

    diagram = VGroup(sub, sub_label, feeder, feeder_label, bus, bus_label, load_line, load, load_label, pv_line, pv_panel, pv_label)

    if show_status:
        status_color = VIOLATION_RED if overloaded else ACCEPTABLE_GREEN
        status_text = "Acima da hosting capacity" if overloaded else "Antes da hosting capacity"
        status = VGroup(
            Text(status_text, font_size=28, color=status_color),
            Text("Tensão aceitável" if not overloaded else "Tensão acima do limite", font_size=22, color=status_color),
            Text("Corrente aceitável" if not overloaded else "Reforços ou controles necessários", font_size=22, color=status_color),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        status.next_to(diagram, DOWN, buff=0.45)
        diagram.add(status)

    diagram.scale(scale)
    return diagram


def make_generation_meter(power_tracker, width=5.8, height=0.28):
    """Create a dynamic distributed generation progress meter."""
    frame = Rectangle(width=width, height=height, color=AUX_GRAY, stroke_width=2)

    fill = always_redraw(
        lambda: Rectangle(
            width=max(0.02, width * power_tracker.get_value() / P_MAX),
            height=height,
            color=PV_ORANGE,
            fill_color=PV_ORANGE,
            fill_opacity=0.85,
            stroke_width=0,
        ).align_to(frame, LEFT).move_to(frame.get_center() + LEFT * (width - max(0.02, width * power_tracker.get_value() / P_MAX)) / 2)
    )

    label = MathTex(r"P_{GD}", font_size=34, color=PV_ORANGE).next_to(frame, LEFT, buff=0.28)
    number = DecimalNumber(0, num_decimal_places=0, font_size=30, color=PV_ORANGE)
    unit = MathTex(r"\mathrm{kW}", font_size=30, color=PV_ORANGE)
    value = VGroup(number, unit).arrange(RIGHT, buff=0.15).next_to(frame, RIGHT, buff=0.32)

    def update_value(mob):
        number.set_value(power_tracker.get_value())
        mob.arrange(RIGHT, buff=0.15).next_to(frame, RIGHT, buff=0.32)

    value.add_updater(update_value)
    return VGroup(frame, fill, label, value)


def make_voltage_indicator(power_tracker, center=ORIGIN):
    """Create a dynamic voltage label and status text."""
    prefix = MathTex(r"V_k=", font_size=38, color=DARK_TEXT)
    number = DecimalNumber(1.00, num_decimal_places=2, font_size=34, color=ACCEPTABLE_GREEN)
    unit = MathTex(r"\mathrm{pu}", font_size=34, color=DARK_TEXT)
    value = VGroup(prefix, number, unit).arrange(RIGHT, buff=0.04)

    ok_status = Text("Tensão dentro do limite", font_size=28, color=ACCEPTABLE_GREEN)
    violation_status = Text("Violação de tensão", font_size=28, color=VIOLATION_RED)
    indicator = VGroup(value, ok_status, violation_status)

    def update_indicator(mob):
        voltage = voltage_from_power(power_tracker.get_value())
        status_color = VIOLATION_RED if voltage > V_LIMIT_HIGH else ACCEPTABLE_GREEN
        number.set_value(voltage)
        number.set_color(status_color)
        value.arrange(RIGHT, buff=0.04)
        ok_status.next_to(value, DOWN, buff=0.18)
        violation_status.move_to(ok_status)
        ok_status.set_opacity(1 if voltage <= V_LIMIT_HIGH else 0)
        violation_status.set_opacity(1 if voltage > V_LIMIT_HIGH else 0)
        mob.move_to(center)

    indicator.add_updater(update_indicator)
    update_indicator(indicator)
    return indicator


def make_voltage_graph():
    """Create the voltage versus distributed generation graph."""
    axes = Axes(
        x_range=[0, 260, 50],
        y_range=[0.94, 1.08, 0.02],
        x_length=8.5,
        y_length=4.35,
        tips=False,
        axis_config={"color": AUX_GRAY, "stroke_width": 2},
        x_axis_config={"include_numbers": True, "font_size": 22},
        y_axis_config={"include_numbers": True, "font_size": 22, "decimal_number_config": {"num_decimal_places": 2}},
    )
    axes.move_to(DOWN * 0.1)

    curve = axes.plot(lambda x: voltage_from_power(x), x_range=[0, P_MAX], color=PV_ORANGE, stroke_width=5)
    upper_limit = DashedLine(axes.c2p(0, V_LIMIT_HIGH), axes.c2p(260, V_LIMIT_HIGH), color=VIOLATION_RED, dash_length=0.15)
    lower_limit = DashedLine(axes.c2p(0, V_LIMIT_LOW), axes.c2p(260, V_LIMIT_LOW), color=ACCEPTABLE_GREEN, dash_length=0.15)
    hc_dot = Dot(axes.c2p(P_HC_V, V_LIMIT_HIGH), color=VIOLATION_RED, radius=0.08)
    hc_line = DashedLine(axes.c2p(P_HC_V, 0.94), axes.c2p(P_HC_V, V_LIMIT_HIGH), color=VIOLATION_RED, dash_length=0.12)

    x_label = VGroup(
        Text("Potência da GD na barra,", font_size=24, color=DARK_TEXT),
        MathTex(r"P_{GD}", font_size=30, color=DARK_TEXT),
    ).arrange(RIGHT, buff=0.12)
    x_label.next_to(axes, DOWN, buff=0.42)
    y_label = VGroup(
        Text("Tensão da barra,", font_size=24, color=DARK_TEXT),
        MathTex(r"V_k", font_size=30, color=DARK_TEXT),
    ).arrange(RIGHT, buff=0.10)
    y_label.rotate(PI / 2).next_to(axes, LEFT, buff=0.45)

    upper_label = MathTex(r"\text{Limite superior: }1.05\,\mathrm{pu}", font_size=25, color=VIOLATION_RED)
    upper_label.move_to(axes.c2p(82, 1.061))
    lower_label = MathTex(r"\text{Limite inferior: }0.95\,\mathrm{pu}", font_size=25, color=ACCEPTABLE_GREEN)
    lower_label.move_to(axes.c2p(82, 0.957))

    hc_label = VGroup(
        Text("Hosting Capacity por tensão", font_size=24, color=VIOLATION_RED),
        MathTex(r"P_{HC,V}=180\,\text{kW}", font_size=34, color=VIOLATION_RED),
    ).arrange(DOWN, buff=0.08)
    hc_label.move_to(axes.c2p(195, 1.078))

    graph = VGroup(axes, curve, upper_limit, lower_limit, hc_dot, hc_line, x_label, y_label, upper_label, lower_label, hc_label)
    return graph


def make_current_indicator(power_tracker, center=ORIGIN):
    """Create a dynamic feeder current loading indicator."""
    frame_width = 4.9
    frame = Rectangle(width=frame_width, height=0.34, color=AUX_GRAY, stroke_width=2)
    fill = always_redraw(
        lambda: Rectangle(
            width=min(frame_width, frame_width * current_loading_from_power(power_tracker.get_value())),
            height=0.34,
            color=VIOLATION_RED if current_loading_from_power(power_tracker.get_value()) > 1 else ACCEPTABLE_GREEN,
            fill_color=VIOLATION_RED if current_loading_from_power(power_tracker.get_value()) > 1 else ACCEPTABLE_GREEN,
            fill_opacity=0.85,
            stroke_width=0,
        ).align_to(frame, LEFT).move_to(
            frame.get_center()
            + LEFT * (frame_width - min(frame_width, frame_width * current_loading_from_power(power_tracker.get_value()))) / 2
        )
    )
    limit_mark = Line(UP * 0.32, DOWN * 0.32, color=VIOLATION_RED, stroke_width=3).next_to(frame, RIGHT, buff=0)
    bar = VGroup(frame, fill, limit_mark)
    title = Text("Carregamento térmico do alimentador", font_size=24, color=DARK_TEXT)
    label = MathTex(r"I_{\text{linha}}/I_{\mathrm{max}}", font_size=30, color=NETWORK_BLUE)
    value = DecimalNumber(0, num_decimal_places=3, font_size=30, color=ACCEPTABLE_GREEN)
    status = Text("Corrente dentro do limite", font_size=26, color=ACCEPTABLE_GREEN)
    violation = Text("Limite térmico do alimentador", font_size=26, color=VIOLATION_RED)
    violation.set_opacity(0)
    readout = VGroup(label, value).arrange(RIGHT, buff=0.22)
    group = VGroup(title, bar, readout, status, violation).arrange(DOWN, buff=0.22)

    def update_group(mob):
        loading = current_loading_from_power(power_tracker.get_value())
        is_violation = loading > 1
        value.set_value(loading)
        value.set_color(VIOLATION_RED if is_violation else ACCEPTABLE_GREEN)
        status.set_opacity(0 if is_violation else 1)
        violation.set_opacity(1 if is_violation else 0)
        readout.arrange(RIGHT, buff=0.22)
        mob.arrange(DOWN, buff=0.22).move_to(center)

    group.add_updater(update_group)
    update_group(group)
    return group


def make_reverse_flow_indicator(power_tracker, center=ORIGIN):
    """Create a dynamic reverse power flow indicator."""
    frame_width = 4.9
    frame = Rectangle(width=frame_width, height=0.34, color=AUX_GRAY, stroke_width=2)
    fill = always_redraw(
        lambda: Rectangle(
            width=min(frame_width, frame_width * reverse_power_from_generation(power_tracker.get_value()) / P_REVERSE_LIMIT),
            height=0.34,
            color=VIOLATION_RED if reverse_power_from_generation(power_tracker.get_value()) > P_REVERSE_LIMIT else PV_ORANGE,
            fill_color=VIOLATION_RED if reverse_power_from_generation(power_tracker.get_value()) > P_REVERSE_LIMIT else PV_ORANGE,
            fill_opacity=0.85,
            stroke_width=0,
        ).align_to(frame, LEFT).move_to(
            frame.get_center()
            + LEFT
            * (
                frame_width
                - min(frame_width, frame_width * reverse_power_from_generation(power_tracker.get_value()) / P_REVERSE_LIMIT)
            )
            / 2
        )
    )
    limit_mark = Line(UP * 0.32, DOWN * 0.32, color=VIOLATION_RED, stroke_width=3).next_to(frame, RIGHT, buff=0)
    bar = VGroup(frame, fill, limit_mark)
    title = Text("Fluxo reverso para a subestação", font_size=24, color=DARK_TEXT)
    label = MathTex(r"P_{\text{reverso}}=", font_size=30, color=PV_ORANGE)
    value = DecimalNumber(0, num_decimal_places=0, font_size=30, color=PV_ORANGE)
    unit = MathTex(r"\mathrm{kW}", font_size=30, color=PV_ORANGE)
    status = Text("Sem exceder o limite permitido", font_size=25, color=ACCEPTABLE_GREEN)
    violation = Text("Limite de fluxo reverso atingido", font_size=25, color=VIOLATION_RED)
    violation.set_opacity(0)
    readout = VGroup(label, value, unit).arrange(RIGHT, buff=0.14)
    group = VGroup(title, bar, readout, status, violation).arrange(DOWN, buff=0.22)

    def update_group(mob):
        reverse_power = reverse_power_from_generation(power_tracker.get_value())
        is_violation = reverse_power > P_REVERSE_LIMIT
        value.set_value(reverse_power)
        value.set_color(VIOLATION_RED if is_violation else PV_ORANGE)
        unit.set_color(VIOLATION_RED if is_violation else PV_ORANGE)
        status.set_opacity(0 if is_violation else 1)
        violation.set_opacity(1 if is_violation else 0)
        readout.arrange(RIGHT, buff=0.14)
        mob.arrange(DOWN, buff=0.22).move_to(center)

    group.add_updater(update_group)
    update_group(group)
    return group


def make_current_limit_scene_elements(power_tracker):
    """Build the visual elements for the current-limit explanation."""
    diagram = make_network_diagram(scale=0.62)
    diagram.move_to(LEFT * 3.85 + UP * 0.4)
    feeder = diagram[2]
    feeder_highlight = Line(feeder.get_start(), feeder.get_end(), color=VIOLATION_RED, stroke_width=9)
    feeder_highlight.set_opacity(0.55)
    indicator = make_current_indicator(power_tracker, center=RIGHT * 3.25 + UP * 0.45)
    meter = make_generation_meter(power_tracker, width=3.55)
    meter.scale(0.82).move_to(DOWN * 2.35)
    condition = VGroup(
        Text("Se", font_size=22, color=VIOLATION_RED),
        MathTex(r"I_{\text{linha}}>I_{\mathrm{max}}", font_size=28, color=VIOLATION_RED),
        Text(", há violação térmica.", font_size=22, color=VIOLATION_RED),
    ).arrange(RIGHT, buff=0.08)
    condition.scale_to_fit_width(4.5)
    explanation = VGroup(
        condition,
        MathTex(r"P_{HC,I}=230\,\text{kW}", font_size=35, color=VIOLATION_RED),
    ).arrange(DOWN, buff=0.16).move_to(RIGHT * 3.25 + DOWN * 1.5)
    note = Text(
        "A corrente aquece o alimentador; mesmo com tensão aceitável, ela pode limitar a conexão.",
        font_size=27,
        color=AUX_GRAY,
    )
    note.scale_to_fit_width(11.5).to_edge(DOWN, buff=0.38)
    return VGroup(diagram, feeder_highlight, indicator, meter, explanation, note)


def make_reverse_flow_scene_elements(power_tracker):
    """Build the visual elements for the reverse-flow explanation."""
    diagram = make_network_diagram(scale=0.62)
    diagram.move_to(LEFT * 3.85 + UP * 0.35)
    reverse_arrow = make_power_arrow(LEFT * 2.45 + UP * 0.9, LEFT * 5.8 + UP * 0.9, "Fluxo reverso", VIOLATION_RED)
    reverse_arrow.scale(0.9)
    reverse_arrow.shift(LEFT * 0.45)
    indicator = make_reverse_flow_indicator(power_tracker, center=RIGHT * 3.25 + UP * 1.08)
    meter = make_generation_meter(power_tracker, width=3.0)
    meter.scale(0.82).move_to(RIGHT * 0.55 + DOWN * 2.55)
    explanation = VGroup(
        Text("Quando a GD excede a carga local,", font_size=21, color=DARK_TEXT),
        Text("a potência reversa volta para a subestação.", font_size=21, color=DARK_TEXT),
        MathTex(r"P_{\text{reverso}}=P_{GD}-P_{\text{carga}}", font_size=30, color=PV_ORANGE),
        MathTex(r"P_{HC,R}=210\,\text{kW}", font_size=35, color=VIOLATION_RED),
    ).arrange(DOWN, buff=0.10).move_to(RIGHT * 3.25 + DOWN * 1.48)
    load_note = Text("Exemplo didático: carga local = 80 kW", font_size=24, color=AUX_GRAY)
    load_note.scale_to_fit_width(4.3).move_to(LEFT * 3.35 + DOWN * 1.55)
    return VGroup(diagram, reverse_arrow, indicator, meter, explanation, load_note)


def make_constraints_panel():
    """Build the panel with operating constraints and final hosting capacity."""
    title = Text("Limites técnicos avaliados", font_size=34, color=DARK_TEXT)

    rows = VGroup(
        VGroup(Text("Tensão (V):", font_size=26, color=DARK_TEXT), MathTex(r"0.95 \leq V_k \leq 1.05\ \text{pu}", font_size=32, color=DARK_TEXT)).arrange(RIGHT, buff=0.25),
        VGroup(Text("Corrente (I):", font_size=26, color=DARK_TEXT), MathTex(r"I_{\text{linha}} \leq I_{\mathrm{max}}", font_size=32, color=DARK_TEXT)).arrange(RIGHT, buff=0.25),
        VGroup(Text("Fluxo reverso (R):", font_size=26, color=DARK_TEXT), MathTex(r"P_{\text{reverso}} \leq \text{limite permitido}", font_size=32, color=DARK_TEXT)).arrange(RIGHT, buff=0.25),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.28)

    limits = VGroup(
        MathTex(r"P_{HC,V}=180\,\text{kW}", font_size=32, color=VIOLATION_RED),
        MathTex(r"P_{HC,I}=230\,\text{kW}", font_size=32, color=ACCEPTABLE_GREEN),
        MathTex(r"P_{HC,R}=210\,\text{kW}", font_size=32, color=ACCEPTABLE_GREEN),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)

    min_formula = MathTex(r"HC=\min(180,230,210)\,\text{kW}", font_size=38, color=DARK_TEXT)
    result = MathTex(r"HC=180\,\text{kW}", font_size=46, color=VIOLATION_RED)
    message = Text("A restrição mais severa define a hosting capacity.", font_size=30, color=VIOLATION_RED)

    left = VGroup(title, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
    right = VGroup(Text("Limites por restrição", font_size=30, color=DARK_TEXT), limits).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
    top = VGroup(left, right).arrange(RIGHT, buff=1.0, aligned_edge=UP)
    bottom = VGroup(min_formula, result, message).arrange(DOWN, buff=0.28)
    panel = VGroup(top, bottom).arrange(DOWN, buff=0.55)

    border = SurroundingRectangle(panel, color=AUX_GRAY, buff=0.28, stroke_width=2)
    return VGroup(border, panel)


def make_solution_balloons():
    """Create compact engineering solution labels."""
    labels = [
        (("Controle", "Volt-VAR"), RIGHT * 3.10 + DOWN * 2.55),
        (("Recondutoramento",), RIGHT * 4.95 + DOWN * 2.55),
        (("Regulador", "de tensão"), RIGHT * 3.10 + DOWN * 3.05),
        (("Armazenamento",), RIGHT * 4.95 + DOWN * 3.05),
        (("Limitação", "de injeção"), RIGHT * 4.05 + DOWN * 3.55),
    ]
    balloons = VGroup()
    for lines, position in labels:
        label = VGroup(*[Text(line, font_size=14, color=DARK_TEXT) for line in lines]).arrange(DOWN, buff=0.02)
        box = RoundedRectangle(corner_radius=0.08, width=label.width + 0.24, height=label.height + 0.14, color=AUX_GRAY, fill_color=BLACK, fill_opacity=0.35, stroke_width=1.5)
        box.move_to(label.get_center())
        item = VGroup(box, label).move_to(position)
        balloons.add(item)
    return balloons


def make_final_formula():
    """Create the final definition and constrained optimization formula."""
    definition_line = VGroup(
        Text("Hosting Capacity = maior", font_size=34, color=DARK_TEXT),
        MathTex(r"P_{GD}", font_size=42, color=DARK_TEXT),
        Text("conectável", font_size=34, color=DARK_TEXT),
    ).arrange(RIGHT, buff=0.14)
    definition_line.scale_to_fit_width(10.4)
    definition = VGroup(
        definition_line,
        Text("respeitando todos os limites operacionais.", font_size=34, color=DARK_TEXT),
    ).arrange(DOWN, buff=0.12)

    formula = VGroup(
        MathTex(r"HC_k=\max P_{GD}", font_size=40, color=PV_ORANGE),
        Text("sujeito a:", font_size=30, color=DARK_TEXT),
        MathTex(r"0.95 \leq V_k \leq 1.05", font_size=40, color=ACCEPTABLE_GREEN),
        MathTex(r"I_{\text{linha}} \leq I_{\mathrm{max}}", font_size=40, color=ACCEPTABLE_GREEN),
        MathTex(r"P_{\text{reverso}} \leq \text{limite permitido}", font_size=36, color=ACCEPTABLE_GREEN),
    ).arrange(DOWN, buff=0.22)

    closing = Text("É uma medida da capacidade da rede de receber geração distribuída.", font_size=30, color=NETWORK_BLUE)
    closing.scale_to_fit_width(11.5)
    return VGroup(definition, formula, closing).arrange(DOWN, buff=0.55)


class HostingCapacityBus(Scene):
    """Animate the hosting capacity concept for a distribution-system bus."""

    def construct(self):
        self.camera.background_color = "#111827"
        self.make_title_scene()
        self.make_system_scene()
        self.animate_generation_ramp()
        self.make_graph_scene()
        self.make_current_limit_scene()
        self.make_reverse_flow_scene()
        self.make_constraints_scene()
        self.make_physical_interpretation()
        self.make_closing_scene()

    def make_title_scene(self):
        title = Text("Hosting Capacity de uma Barra", font_size=48, color=NETWORK_BLUE)
        title.to_edge(UP, buff=0.7)

        line_1 = Text("Máxima geração distribuída", font_size=34, color=PV_ORANGE)
        line_2 = Text("que pode ser conectada", font_size=30, color=DARK_TEXT)
        line_3 = Text("sem violar limites técnicos.", font_size=34, color=ACCEPTABLE_GREEN)
        definition = VGroup(line_1, line_2, line_3).arrange(DOWN, buff=0.18)
        definition.move_to(ORIGIN)

        highlight_1 = SurroundingRectangle(line_1, color=PV_ORANGE, buff=0.12, stroke_width=3)
        highlight_2 = SurroundingRectangle(line_3, color=ACCEPTABLE_GREEN, buff=0.12, stroke_width=3)

        self.play(FadeIn(title, shift=DOWN * 0.25), run_time=1.4)
        self.play(FadeIn(definition, shift=UP * 0.25), run_time=1.6)
        self.play(Create(highlight_1), Indicate(line_1, color=PV_ORANGE), run_time=1.4)
        self.play(Create(highlight_2), Indicate(line_3, color=ACCEPTABLE_GREEN), run_time=1.4)
        self.wait(3.0)
        self.play(FadeOut(VGroup(title, definition, highlight_1, highlight_2)), run_time=1.1)

    def make_system_scene(self):
        title = Text("Sistema elétrico simplificado", font_size=40, color=DARK_TEXT).to_edge(UP, buff=0.35)
        diagram = make_network_diagram(scale=0.95)
        diagram.move_to(DOWN * 0.15)

        sub_to_load = make_power_arrow(LEFT * 3.6 + UP * 0.65, LEFT * 0.1 + UP * 0.65, "Potência da subestação", NETWORK_BLUE)
        sub_to_load.scale(0.85)
        gd_injection = make_power_arrow(RIGHT * 3.0 + UP * 1.75, RIGHT * 1.55 + UP * 0.72, "Injeção da GD", PV_ORANGE)
        gd_injection.scale(0.85)
        gd_injection.shift(DOWN * 0.30)

        self.play(FadeIn(title), run_time=0.8)
        self.play(Create(diagram), run_time=2.4)
        self.play(GrowArrow(sub_to_load[0]), FadeIn(sub_to_load[1]), run_time=1.5)
        self.wait(1.2)
        self.play(GrowArrow(gd_injection[0]), FadeIn(gd_injection[1]), run_time=1.5)
        self.wait(3.0)
        self.play(FadeOut(VGroup(title, diagram, sub_to_load, gd_injection)), run_time=1.0)

    def animate_generation_ramp(self):
        title = Text("Aumento gradual da geração distribuída", font_size=38, color=DARK_TEXT).to_edge(UP, buff=0.35)
        power_tracker = ValueTracker(0)

        meter = make_generation_meter(power_tracker)
        meter.move_to(UP * 1.0)

        voltage_indicator = make_voltage_indicator(power_tracker, center=DOWN * 0.2)

        limit_text = MathTex(r"V_{\max}=1.05\ \text{pu}", font_size=36, color=VIOLATION_RED)
        limit_text.next_to(voltage_indicator, DOWN, buff=0.55)

        note = VGroup(
            Text("À medida que", font_size=28, color=AUX_GRAY),
            MathTex(r"P_{GD}", font_size=34, color=AUX_GRAY),
            Text("aumenta, a tensão da barra tende a subir.", font_size=28, color=AUX_GRAY),
        ).arrange(RIGHT, buff=0.12)
        note.scale_to_fit_width(11.4)
        note.to_edge(DOWN, buff=0.55)

        self.play(FadeIn(title), FadeIn(meter), FadeIn(voltage_indicator), FadeIn(limit_text), FadeIn(note), run_time=1.2)
        self.wait(1.2)

        ramp_values = [50, 100, 150, P_HC_V, 200, 250]
        for target in ramp_values:
            run_time = 1.5 if target != P_HC_V else 1.0
            self.play(power_tracker.animate.set_value(target), run_time=run_time, rate_func=smooth)
            if target == P_HC_V:
                self.play(Indicate(limit_text, color=VIOLATION_RED), run_time=0.9)
            if target > P_HC_V:
                self.play(Indicate(voltage_indicator, color=VIOLATION_RED), run_time=0.9)
            self.wait(0.65)

        self.wait(2.5)
        self.play(FadeOut(VGroup(title, meter, voltage_indicator, limit_text, note)), run_time=1.0)

    def make_graph_scene(self):
        title = Text("Tensão versus geração distribuída", font_size=38, color=DARK_TEXT).to_edge(UP, buff=0.35)
        graph = make_voltage_graph()
        graph.scale(0.9).shift(DOWN * 0.1)

        axes, curve, upper_limit, lower_limit, hc_dot, hc_line = graph[0], graph[1], graph[2], graph[3], graph[4], graph[5]
        labels = VGroup(*graph[6:])

        self.play(FadeIn(title), Create(axes), FadeIn(labels[0]), FadeIn(labels[1]), run_time=1.5)
        self.play(Create(lower_limit), FadeIn(labels[3]), Create(upper_limit), FadeIn(labels[2]), run_time=1.4)
        self.play(Create(curve), run_time=2.8)
        self.play(FadeIn(hc_dot), Create(hc_line), FadeIn(labels[4]), run_time=1.4)
        self.play(Indicate(hc_dot, color=VIOLATION_RED), Indicate(labels[4], color=VIOLATION_RED), run_time=1.2)
        self.wait(3.5)
        self.play(FadeOut(VGroup(title, graph)), run_time=1.0)

    def make_current_limit_scene(self):
        title = Text("Hosting Capacity por corrente", font_size=38, color=DARK_TEXT).to_edge(UP, buff=0.35)
        power_tracker = ValueTracker(0)
        elements = make_current_limit_scene_elements(power_tracker)
        diagram, feeder_highlight, indicator, meter, explanation, note = elements

        self.play(FadeIn(title), FadeIn(diagram), FadeIn(indicator), FadeIn(meter), FadeIn(note), run_time=1.2)
        self.play(FadeIn(feeder_highlight), run_time=0.8)
        self.wait(0.6)

        for target in [100, 180, P_HC_I, 250]:
            self.play(power_tracker.animate.set_value(target), run_time=1.4, rate_func=smooth)
            if target == P_HC_I:
                self.play(FadeIn(explanation[0]), FadeIn(explanation[1]), run_time=0.8)
                self.play(Indicate(explanation[1], color=VIOLATION_RED), run_time=0.8)
            if target > P_HC_I:
                self.play(Indicate(indicator, color=VIOLATION_RED), run_time=0.9)
            self.wait(0.45)

        self.wait(1.6)
        self.play(FadeOut(VGroup(title, elements)), run_time=1.0)

    def make_reverse_flow_scene(self):
        title = Text("Hosting Capacity por fluxo reverso", font_size=38, color=DARK_TEXT).to_edge(UP, buff=0.35)
        power_tracker = ValueTracker(0)
        elements = make_reverse_flow_scene_elements(power_tracker)
        diagram, reverse_arrow, indicator, meter, explanation, load_note = elements

        self.play(FadeIn(title), FadeIn(diagram), FadeIn(indicator), FadeIn(meter), FadeIn(load_note), run_time=1.2)
        self.play(FadeIn(explanation[0]), FadeIn(explanation[1]), run_time=1.0)

        arrow_shown = False
        for target in [50, 100, 160, P_HC_R, 250]:
            self.play(power_tracker.animate.set_value(target), run_time=1.35, rate_func=smooth)
            if target > P_LOCAL_LOAD and not arrow_shown:
                self.play(GrowArrow(reverse_arrow[0]), FadeIn(reverse_arrow[1]), FadeIn(explanation[2]), run_time=1.0)
                arrow_shown = True
            if target == P_HC_R:
                self.play(FadeIn(explanation[3]), Indicate(explanation[3], color=VIOLATION_RED), run_time=1.0)
            if target > P_HC_R:
                self.play(Indicate(indicator, color=VIOLATION_RED), Indicate(reverse_arrow, color=VIOLATION_RED), run_time=0.9)
            self.wait(0.45)

        self.wait(1.6)
        self.play(FadeOut(VGroup(title, elements)), run_time=1.0)

    def make_constraints_scene(self):
        panel = make_constraints_panel()
        panel.scale_to_fit_width(12.5)

        title = Text("A hosting capacity final considera todos os limites", font_size=36, color=DARK_TEXT)
        title.to_edge(UP, buff=0.32)
        panel.next_to(title, DOWN, buff=0.35)

        result = panel[1][1][1]
        message = panel[1][1][2]

        self.play(FadeIn(title), FadeIn(panel[0]), run_time=0.9)
        self.play(FadeIn(panel[1][0]), run_time=1.4)
        self.play(FadeIn(panel[1][1][0]), run_time=1.0)
        self.play(FadeIn(result), run_time=0.9)
        self.play(Indicate(result, color=VIOLATION_RED), FadeIn(message), run_time=1.2)
        self.wait(3.5)
        self.play(FadeOut(VGroup(title, panel)), run_time=1.0)

    def make_physical_interpretation(self):
        title = Text("Interpretação física na barra", font_size=38, color=DARK_TEXT).to_edge(UP, buff=0.35)
        before = make_network_diagram(scale=0.62, show_status=True, overloaded=False)
        after = make_network_diagram(scale=0.62, show_status=True, overloaded=True)
        before.move_to(LEFT * 3.45 + UP * 0.1)
        after.move_to(RIGHT * 3.45 + UP * 0.1)

        separator = DashedLine(UP * 2.7, DOWN * 1.7, color=AUX_GRAY, dash_length=0.18)
        alert = VGroup(
            Text("Acima da hosting capacity:", font_size=21, color=VIOLATION_RED),
            Text("conexão não recomendada", font_size=19, color=VIOLATION_RED),
            Text("sem reforços ou controles.", font_size=19, color=VIOLATION_RED),
        ).arrange(DOWN, buff=0.03)
        alert.move_to(DOWN * 2.25)
        solutions = make_solution_balloons()

        self.play(FadeIn(title), run_time=0.7)
        self.play(FadeIn(before), Create(separator), run_time=1.5)
        self.play(FadeIn(after), run_time=1.5)
        self.play(Indicate(after, color=VIOLATION_RED), FadeIn(alert), run_time=1.3)
        self.play(LaggedStart(*[FadeIn(item, shift=UP * 0.15) for item in solutions], lag_ratio=0.12), run_time=1.8)
        self.wait(3.5)
        self.play(FadeOut(VGroup(title, before, after, separator, alert, solutions)), run_time=1.0)

    def make_closing_scene(self):
        final_group = make_final_formula()
        final_group.move_to(ORIGIN)

        self.play(FadeIn(final_group[0], shift=DOWN * 0.2), run_time=1.2)
        self.play(Write(final_group[1]), run_time=2.0)
        self.play(FadeIn(final_group[2], shift=UP * 0.2), run_time=1.1)
        self.wait(6.5)
        self.play(Indicate(final_group[0], color=PV_ORANGE), Indicate(final_group[2], color=NETWORK_BLUE), run_time=1.3)
        self.wait(4.0)
