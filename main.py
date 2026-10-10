from pathlib import Path

from manim import *
from PIL import Image

# =========================================================
# 配色方案
# =========================================================
BG_COLOR = "#FAF4E1"  # 暖白书页背景
FG_COLOR = "#3E2723"  # 深棕（前景）
FG_LIGHT = "#6D4C41"  # 浅棕（次要标注）

RED_WARM = "#C62828"  # 暖红
YELLOW_WARM = "#F9A825"  # 暖黄
ORANGE_WARM = "#E65100"  # 深橙
RED_LIGHT = "#EF9A9A"  # 浅红
YELLOW_LIGHT = "#FFE082"  # 浅黄

# 中文字体
CN_FONT = "Noto Serif SC"

# 曲线与矩形的公共取值范围（场景 3/4/5 共用同一坐标系）
T_RANGE = [0, 3]
V_RANGE = [0, 10]


# =========================================================
# 工具函数
# =========================================================
def apply_theme(scene):
    """设置背景色和全局默认前景色。"""
    scene.camera.background_color = BG_COLOR
    Text.set_default(color=FG_COLOR)
    MathTex.set_default(color=FG_COLOR)
    VMobject.set_default(color=FG_COLOR)
    Axes.set_default(axis_config={"color": FG_COLOR, "include_tip": False})


def make_axes(x_range, y_range, x_length, y_length, shift):
    """建立 t-v 坐标系。"""
    return Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=x_length,
        y_length=y_length,
        axis_config={"include_tip": False, "color": FG_COLOR},
    ).shift(shift)


def make_axis_labels(axes):
    """坐标轴的两个中文标签。"""
    x_label = Text("时间 t / s", font=CN_FONT, font_size=26, color=FG_COLOR).next_to(
        axes.x_axis, DOWN, buff=0.3
    )
    y_label = (
        Text("速度 v / (m/s)", font=CN_FONT, font_size=26, color=FG_COLOR)
        .next_to(axes.y_axis, LEFT, buff=0.3)
        .rotate(PI / 2)
    )
    return x_label, y_label


def make_curve(axes, stroke_width=4):
    """v = t^2 曲线。"""
    return axes.plot(
        lambda t: t**2, x_range=T_RANGE, color=RED_WARM, stroke_width=stroke_width
    )


def make_rects(axes, curve, dx=1, stroke_width=1.5):
    """曲线下的黎曼矩形。"""
    return axes.get_riemann_rectangles(
        curve,
        x_range=T_RANGE,
        dx=dx,
        input_sample_type="center",
        stroke_width=stroke_width,
        stroke_color=ORANGE_WARM,
        fill_opacity=0.5,
        color=YELLOW_WARM,
    )


# =========================================================
# 全片：一条连续动画流
# =========================================================
class Jiangti26Q3(Scene):
    def construct(self):
        apply_theme(self)
        self.still_dir = Path(config.get_dir("images_dir", module_name="main"))

        self.part1_intro()
        self.part2_uniform()

        # 场景 3/4/5 共用同一组坐标系、曲线、矩形，逐段传递
        axes, curve, rects = self.part3_variable()
        axes, curve, rects = self.part4_delta_sum(axes, curve, rects)
        self.part5_refine(axes, curve, rects)

        self.part6_extend()
        self.part7_summary()

    def shoot(self, name):
        """把当前画面存成 PNG，作为提交材料用的静帧。"""
        self.still_dir.mkdir(parents=True, exist_ok=True)
        self.renderer.update_frame(self)
        Image.fromarray(self.renderer.get_frame()).save(self.still_dir / f"{name}.png")

    # ---------------------------------------------------------
    # 场景 1：引入
    # ---------------------------------------------------------
    def part1_intro(self):
        title = Text("速度一直在变", font=CN_FONT, font_size=64, color=FG_COLOR)
        question = Text("怎么求总路程？", font=CN_FONT, font_size=64, color=RED_WARM)
        question.next_to(title, DOWN, buff=0.5)

        self.play(Write(title), run_time=1.5)
        self.play(Write(question), run_time=1.5)
        self.wait(1.0)
        self.play(FadeOut(title), FadeOut(question), run_time=0.8)

        # 汽车
        car_body = Rectangle(
            width=1.8, height=0.7, color=RED_WARM, fill_opacity=1.0
        ).shift(LEFT * 3 + DOWN * 0.5)
        wheel1 = Circle(radius=0.2, color=FG_COLOR, fill_opacity=1.0).move_to(
            car_body.get_bottom() + LEFT * 0.5 + DOWN * 0.15
        )
        wheel2 = Circle(radius=0.2, color=FG_COLOR, fill_opacity=1.0).move_to(
            car_body.get_bottom() + RIGHT * 0.5 + DOWN * 0.15
        )
        car = VGroup(car_body, wheel1, wheel2)

        speed_display = Text(
            "0 m/s", font=CN_FONT, font_size=56, color=YELLOW_WARM
        ).shift(RIGHT * 2 + DOWN * 0.5)

        self.play(FadeIn(car), FadeIn(speed_display), run_time=1.0)

        for s in ["3 m/s", "7 m/s", "2 m/s", "9 m/s"]:
            new_display = Text(
                s, font=CN_FONT, font_size=56, color=YELLOW_WARM
            ).move_to(speed_display)
            self.play(Transform(speed_display, new_display), run_time=0.5)

        self.wait(1.5)
        self.shoot("01_intro")

        # 下一段是坐标系，与本段无关，整体淡出
        self.play(FadeOut(car, speed_display), run_time=0.8)

    # ---------------------------------------------------------
    # 场景 2：匀速情况
    # ---------------------------------------------------------
    def part2_uniform(self):
        axes = make_axes([0, 5, 1], [0, 8, 2], 8, 4, DOWN * 0.5)
        x_label, y_label = make_axis_labels(axes)

        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=1.5)

        line = axes.plot(lambda t: 5, x_range=[0, 4], color=RED_WARM, stroke_width=4)
        self.play(Create(line), run_time=1.0)

        rect = Rectangle(
            width=axes.c2p(4, 0)[0] - axes.c2p(0, 0)[0],
            height=axes.c2p(0, 5)[1] - axes.c2p(0, 0)[1],
            color=YELLOW_WARM,
            fill_opacity=0.45,
            stroke_color=YELLOW_WARM,
            stroke_width=2,
        )
        rect.move_to(axes.c2p(2, 2.5))
        self.play(FadeIn(rect), run_time=1.0)

        formula = MathTex(
            r"S = v \cdot t = 5 \times 4 = 20\ \text{m}",
            font_size=48,
            color=FG_COLOR,
        )
        formula.to_edge(UP, buff=1.2)
        self.play(Write(formula), run_time=1.5)

        self.wait(2.0)
        self.shoot("02_uniform")

        # 坐标范围与场景 3 不同，整套淡出后重画
        self.play(
            FadeOut(axes, x_label, y_label, line, rect, formula), run_time=0.8
        )

    # ---------------------------------------------------------
    # 场景 3：变速切分
    # ---------------------------------------------------------
    def part3_variable(self):
        axes = make_axes([0, 3.5, 1], V_RANGE, 7.5, 4.5, DOWN * 0.3)
        x_label, y_label = make_axis_labels(axes)

        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=1.2)

        curve = make_curve(axes)
        self.play(Create(curve), run_time=1.5)

        formula = MathTex(r"v = t^2", font_size=44, color=RED_WARM)
        formula.to_corner(UR).shift(LEFT * 0.6 + DOWN * 1.0)
        self.play(Write(formula), run_time=0.8)

        rects = make_rects(axes, curve)
        self.play(Create(rects), run_time=2.0)

        note = Text(
            "切成 3 段，每段近似匀速", font=CN_FONT, font_size=30, color=ORANGE_WARM
        ).to_edge(UP, buff=0.6)
        self.play(FadeIn(note), run_time=1.0)

        self.wait(2.0)
        self.shoot("03_variable")

        # 只把坐标系、曲线、矩形交给下一场，标注先退场
        self.play(FadeOut(formula, note, x_label, y_label), run_time=0.8)
        return axes, curve, rects

    # ---------------------------------------------------------
    # 场景 4：Δ 与 Σ
    # ---------------------------------------------------------
    def part4_delta_sum(self, axes, curve, rects):
        # 同一张图：坐标系缩小左移给右侧公式腾地方，曲线和矩形跟着一起变形
        wide_axes = make_axes(
            [0, 3.5, 1], V_RANGE, 6.5, 4.2, LEFT * 3.2 + DOWN * 0.3
        )
        wide_curve = make_curve(wide_axes, stroke_width=3)
        wide_rects = make_rects(wide_axes, wide_curve)

        self.play(
            Transform(axes, wide_axes),
            Transform(curve, wide_curve),
            Transform(rects, wide_rects),
            run_time=1.2,
        )
        # Transform 后原对象已具有新坐标，继续沿用即可（下方 c2p 均按新坐标计算）

        self.play(rects[1].animate.set_fill(opacity=0.85), run_time=0.5)

        brace = Brace(Line(axes.c2p(1, 0), axes.c2p(2, 0)), DOWN, buff=0.1)
        dt_label = MathTex(r"\Delta t = 1", font_size=34, color=YELLOW_WARM)
        dt_label.next_to(brace, DOWN, buff=0.1)
        self.play(GrowFromCenter(brace), Write(dt_label), run_time=1.0)

        h_line = DashedLine(
            axes.c2p(1.5, 0), axes.c2p(1.5, 2.25), color=RED_WARM, stroke_width=2
        )
        h_label = MathTex(r"v_i", font_size=36, color=RED_WARM).next_to(
            h_line, RIGHT, buff=0.1
        )
        self.play(Create(h_line), Write(h_label), run_time=0.8)

        self.wait(0.5)

        f1 = MathTex(
            r"\Delta S_i \approx v_i \cdot \Delta t", font_size=40, color=FG_COLOR
        )
        f1.to_edge(RIGHT, buff=0.8).shift(UP * 1.5)
        self.play(Write(f1), run_time=1.0)

        self.wait(0.5)

        f2 = MathTex(
            r"S \approx \sum_{i=1}^{n} v_i \cdot \Delta t",
            font_size=44,
            color=ORANGE_WARM,
        )
        f2.next_to(f1, DOWN, buff=0.7).align_to(f1, LEFT)
        self.play(Write(f2), run_time=1.5)

        note1 = Text("Δ：变化量", font=CN_FONT, font_size=26, color=FG_LIGHT)
        note2 = Text("Σ：求和", font=CN_FONT, font_size=26, color=FG_LIGHT)
        notes = VGroup(note1, note2).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        notes.next_to(f2, DOWN, buff=0.6).align_to(f2, LEFT)

        self.play(FadeIn(notes), run_time=1.0)

        self.wait(2.0)
        self.shoot("04_delta_sum")

        # 标注退场，坐标系/曲线/矩形留给下一场继续变形
        self.play(
            FadeOut(brace, dt_label, h_line, h_label, f1, f2, notes), run_time=0.8
        )
        return axes, curve, rects

    # ---------------------------------------------------------
    # 场景 5：切得更细
    # ---------------------------------------------------------
    def part5_refine(self, axes, curve, rects):
        # 坐标系回到居中放大；曲线和矩形必须跟着同一次变形，
        # 否则矩形会停在旧位置，和坐标轴、曲线脱节
        full_axes = make_axes([0, 3.5, 1], V_RANGE, 7.5, 4.5, DOWN * 0.3)
        full_curve = make_curve(full_axes)
        full_rects = make_rects(full_axes, full_curve)
        self.play(
            Transform(axes, full_axes),
            Transform(curve, full_curve),
            Transform(rects, full_rects),
            run_time=1.2,
        )
        # Transform 只改原对象的形状，rects 仍是屏幕上那一个，
        # 矩形 2 的高亮也会在这次变形中自动复位

        n_label = Text(
            "切成 3 段", font=CN_FONT, font_size=30, color=ORANGE_WARM
        ).to_edge(UP, buff=0.6)
        self.play(FadeIn(n_label))
        self.wait(1.0)

        for n, dx in [(6, 0.5), (12, 0.25), (30, 0.1)]:
            new_rects = make_rects(full_axes, full_curve, dx=dx, stroke_width=1)
            new_label = Text(
                f"切成 {n} 段", font=CN_FONT, font_size=30, color=ORANGE_WARM
            ).to_edge(UP, buff=0.6)

            self.play(
                ReplacementTransform(rects, new_rects),
                Transform(n_label, new_label),
                run_time=1.5,
            )
            rects = new_rects
            self.wait(0.8)

        area = full_axes.get_area(
            full_curve, x_range=T_RANGE, color=RED_LIGHT, opacity=0.35
        )
        self.play(FadeIn(area), run_time=1.5)

        final_text = Text(
            "矩形面积和 ≈ 曲线下面积 = 总路程",
            font=CN_FONT,
            font_size=32,
            color=FG_COLOR,
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(final_text), run_time=1.0)

        self.wait(2.0)
        self.shoot("05_refine")

        # 图形部分与总结无关，整体淡出
        self.play(
            FadeOut(
                axes, curve, rects, area, n_label, final_text
            ),
            run_time=0.8,
        )

    # ---------------------------------------------------------
    # 场景 6：推广
    # ---------------------------------------------------------
    def part6_extend(self):
        title = Text(
            "同样的思想，不同的量", font=CN_FONT, font_size=44, color=FG_COLOR
        ).to_edge(UP, buff=0.8)
        self.play(Write(title), run_time=1.0)

        texts = [
            ("速度 × 时间", "路程"),
            ("流量 × 时间", "水量"),
            ("功率 × 时间", "电能"),
        ]

        cards = VGroup()
        for top, bottom in texts:
            card = RoundedRectangle(
                width=3.5,
                height=2.2,
                corner_radius=0.2,
                color=YELLOW_WARM,
                stroke_width=2,
                fill_color=YELLOW_LIGHT,
                fill_opacity=0.3,
            )
            t1 = Text(top, font=CN_FONT, font_size=26, color=FG_COLOR).move_to(
                card.get_center() + UP * 0.55
            )
            t2 = Text("=", font=CN_FONT, font_size=30, color=FG_COLOR).move_to(
                card.get_center() + UP * 0.05
            )
            t3 = Text(bottom, font=CN_FONT, font_size=36, color=RED_WARM).move_to(
                card.get_center() + DOWN * 0.55
            )
            cards.add(VGroup(card, t1, t2, t3))

        cards.arrange(RIGHT, buff=0.6).shift(DOWN * 0.3)

        for card in cards:
            self.play(FadeIn(card, shift=UP * 0.3), run_time=0.7)
            self.wait(0.4)

        note = Text(
            "曲线下的面积 = 累积量", font=CN_FONT, font_size=32, color=ORANGE_WARM
        ).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(note), run_time=1.0)

        self.wait(2.0)
        self.shoot("06_extend")

        # 总结页另起内容，整体淡出
        self.play(FadeOut(title, cards, note), run_time=0.8)

    # ---------------------------------------------------------
    # 场景 7：总结
    # ---------------------------------------------------------
    def part7_summary(self):
        k1 = Text("切碎", font=CN_FONT, font_size=64, color=RED_WARM)
        k2 = Text("近似", font=CN_FONT, font_size=64, color=YELLOW_WARM)
        k3 = Text("累加", font=CN_FONT, font_size=64, color=ORANGE_WARM)

        keywords = VGroup(k1, k2, k3).arrange(RIGHT, buff=1.2)

        self.play(Write(k1), run_time=0.8)
        self.play(Write(k2), run_time=0.8)
        self.play(Write(k3), run_time=0.8)
        self.wait(1.5)

        self.play(FadeOut(keywords))

        s1 = Text(
            "把变化切成小段，每段近似不变，再累加。",
            font=CN_FONT,
            font_size=36,
            color=FG_COLOR,
        ).shift(UP * 1.0)
        s2 = Text(
            "这就是积分思想。", font=CN_FONT, font_size=36, color=ORANGE_WARM
        ).shift(UP * 0.1)
        s3 = Text(
            "量，可以由变化累积出来。",
            font=CN_FONT,
            font_size=32,
            color=FG_LIGHT,
        ).shift(DOWN * 0.8)

        self.play(Write(s1), run_time=1.5)
        self.play(Write(s2), run_time=1.0)
        self.play(Write(s3), run_time=1.0)
        self.wait(1.0)

        integral = MathTex(
            r"S = \int_0^T v(t)\,dt", font_size=60, color=RED_WARM
        ).shift(DOWN * 2.0)
        self.play(Write(integral), run_time=1.5)

        self.wait(2.0)
        self.shoot("07_summary")