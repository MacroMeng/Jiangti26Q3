"""速度—时间图像求路程的动画讲解。

整支片子渲染成一个连续 Scene（Jiangti26Q3），不再拆成多段各自成片。
每一段是一个 partN_* 方法，按顺序在 construct() 里调用。

片子围绕一个具体例题展开：

    求 y = x² 在 0 ≤ x ≤ 3 下与 x 轴围成的面积

先把这个纯数学问题「翻译」成 v-t 图下的面积（即路程），再用原来的结构
（匀速 → 切分 → Δ 与 Σ）讲清方法，最后用左右端点夹逼逼出答案 9，
并回到「切碎 / 近似 / 累加」的总结。

全程只用一套坐标系（0 ≤ t ≤ 3，0 ≤ v ≤ 10），所以段与段之间的衔接
都是同一组物体的变形，不存在硬切。
"""

from pathlib import Path

from manim import *
from PIL import Image

# =========================================================
# 配色方案
# =========================================================
BG_COLOR = "#FAF4E1"  # 暖白书页背景
FG_COLOR = "#3E2723"  # 深棕（前景，正文）
FG_LIGHT = "#6D4C41"  # 浅棕（次要标注）

RED_WARM = "#C62828"  # 暖红（标题、曲线）
ORANGE_WARM = "#E65100"  # 深橙（强调）
RED_LIGHT = "#EF9A9A"  # 浅红（低估区域填充）
YELLOW_WARM = "#F9A825"  # 暖黄（矩形填充，不用于文字）
YELLOW_LIGHT = "#FFE082"  # 浅黄（面积高亮）
RECT_STROKE = "#8C3B1F"  # 深赭（矩形描边，比填充深得多）

# 中文字体
CN_FONT = "Noto Serif SC"

# 坐标系统一取值：例题是 0 ≤ x ≤ 3，曲线 v = t² 最高到 9
T_MAX = 3
V_MAX = 10
T_STEP = 1
V_STEP = 2

# 坐标系位置。整体略高于中心，把画面下方让给文字，
# 否则底部文字会压到 x 轴的刻度数字上。
MAIN_SHIFT = UP * 0.25
# 左侧栏的偏移要留出轴名「v / (m/s)」的宽度，否则会被画面左边缘裁掉
SIDE_SHIFT = LEFT * 2.8 + UP * 0.15


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


def make_axes(x_length, y_length, shift):
    """建立唯一的 t-v 坐标系。刻度数字只标关键值，0 省略。"""
    return Axes(
        x_range=[0, T_MAX + 0.5, T_STEP],
        y_range=[0, V_MAX, V_STEP],
        x_length=x_length,
        y_length=y_length,
        axis_config={
            "include_tip": False,
            "include_numbers": True,
            "numbers_to_exclude": [0],
            "font_size": 24,
            "color": FG_COLOR,
            "stroke_width": 2,
        },
    ).shift(shift)


def make_curve(axes, stroke_width=4):
    """v = t² 曲线（例题里的 y = x² 是同一条曲线）。"""
    return axes.plot(
        lambda t: t**2, x_range=[0, T_MAX], color=RED_WARM, stroke_width=stroke_width
    )


def make_rects(
    axes,
    curve,
    dx=1,
    sample="center",
    fill=YELLOW_WARM,
    stroke=RECT_STROKE,
    opacity=0.5,
    stroke_width=2.5,
):
    """曲线下的黎曼矩形。"""
    return axes.get_riemann_rectangles(
        curve,
        x_range=[0, T_MAX],
        dx=dx,
        input_sample_type=sample,
        stroke_width=stroke_width,
        stroke_color=stroke,
        fill_opacity=opacity,
        color=fill,
    )


def make_axis_names(axes):
    """坐标轴名。part1 用纯数学的 x / y，part2 换成带单位的 t / v。"""
    x_name = Text("x", font=CN_FONT, font_size=32, color=FG_COLOR)
    x_name.next_to(axes.x_axis.get_end(), DR, buff=0.15)
    y_name = Text("y", font=CN_FONT, font_size=32, color=FG_COLOR)
    # 放在轴顶端正上方，避开刻度数字「10」
    y_name.next_to(axes.y_axis.get_end(), UP, buff=0.25)
    return x_name, y_name


# =========================================================
# 全片：一条连续动画流
# =========================================================
class Jiangti26Q3(Scene):
    def construct(self):
        apply_theme(self)
        self.still_dir = Path(config.get_dir("images_dir", module_name="main"))

        # 抛出例题
        axes, x_name, y_name, curve, region, hook, question = self.part1_problem()

        # 把纯数学问题翻译成 v-t 图下的面积
        axes, x_name, y_name, curve, region = self.part2_convert(
            axes, x_name, y_name, curve, region, hook, question
        )

        # 以下沿用原片结构
        axes, x_name, y_name, curve, region = self.part3_uniform(
            axes, x_name, y_name, curve, region
        )
        axes, x_name, y_name, curve, region, rects = self.part4_cut(
            axes, x_name, y_name, curve, region
        )
        axes, x_name, y_name, curve, region, rects = self.part5_delta_sum(
            axes, x_name, y_name, curve, region, rects
        )
        axes, x_name, y_name, curve, region = self.part6_squeeze(
            axes, x_name, y_name, curve, rects, region
        )
        # 图表部分到此为止，后面两段是纯文字，不需要再把物体往下传
        self.part7_answer(axes, x_name, y_name, curve, region)

        self.part8_extend()
        self.part9_summary()

    # ---------------------------------------------------------
    # 通用
    # ---------------------------------------------------------
    def shoot(self, name):
        """把当前画面存成 PNG，作为提交材料用的静帧。"""
        self.still_dir.mkdir(parents=True, exist_ok=True)
        self.renderer.update_frame(self)
        Image.fromarray(self.renderer.get_frame()).save(self.still_dir / f"{name}.png")

    def clear_except(self, *keep, run_time=0.8):
        """淡出屏幕上除 keep 之外的所有物体。"""
        doomed = [m for m in self.mobjects if not any(m is k for k in keep)]
        if doomed:
            self.play(FadeOut(*doomed), run_time=run_time)

    # ---------------------------------------------------------
    # 场景 1：抛出例题
    # ---------------------------------------------------------
    def part1_problem(self):
        axes = make_axes(7.5, 4.5, MAIN_SHIFT)
        x_name, y_name = make_axis_names(axes)

        self.play(Create(axes), FadeIn(x_name), FadeIn(y_name), run_time=1.2)

        curve = make_curve(axes)
        self.play(Create(curve), run_time=1.5)

        region = axes.get_area(
            curve, x_range=[0, T_MAX], color=YELLOW_LIGHT, opacity=0.5
        )
        self.play(FadeIn(region), run_time=1.0)

        # 开场用自然语言把问题说清楚，不用积分符号
        question = VGroup(
            Text("例题：求曲线 y = x² 与 x 轴", font=CN_FONT, font_size=30, color=FG_COLOR),
            Text("在 0 ≤ x ≤ 3 上围成的面积", font=CN_FONT, font_size=30, color=RED_WARM),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT).to_edge(UP, buff=0.6)
        self.play(FadeIn(question, shift=DOWN * 0.2), run_time=1.2)

        hook = Text("怎么算？", font=CN_FONT, font_size=30, color=FG_COLOR).to_edge(
            DOWN, buff=0.5
        )
        self.play(FadeIn(hook), run_time=0.8)

        self.wait(2.0)
        self.shoot("01_problem")

        return axes, x_name, y_name, curve, region, hook, question

    # ---------------------------------------------------------
    # 场景 2：转换成 v-t 图
    # ---------------------------------------------------------
    def part2_convert(self, axes, x_name, y_name, curve, region, hook, question):
        self.play(FadeOut(hook), run_time=0.6)

        # 坐标轴换名：同一块面积，从几何问题变成物理问题
        new_x = Text("t / s", font=CN_FONT, font_size=28, color=FG_COLOR)
        new_x.next_to(axes.x_axis.get_end(), DR, buff=0.15)
        new_y = Text("v / (m/s)", font=CN_FONT, font_size=28, color=FG_COLOR)
        new_y.next_to(axes.y_axis.get_end(), UP, buff=0.25)
        self.play(Transform(x_name, new_x), Transform(y_name, new_y), run_time=0.8)

        identity = Text(
            "同一个面积，换一副坐标看", font=CN_FONT, font_size=28, color=ORANGE_WARM
        ).next_to(question, DOWN, buff=0.4)
        self.play(FadeIn(identity), run_time=0.8)

        # MathTex 里不能放中文（xelatex 模板不支持），中文一律用 Text。
        # 等号也用 Text，保证与两侧中文同一字体、同一高度。
        claim = VGroup(
            Text("曲线下的面积", font=CN_FONT, font_size=38, color=FG_COLOR),
            Text("＝", font=CN_FONT, font_size=38, color=FG_COLOR),
            Text("总路程", font=CN_FONT, font_size=38, color=RED_WARM),
        ).arrange(RIGHT, buff=0.5)
        claim.to_edge(DOWN, buff=0.5)
        self.play(Write(claim), run_time=1.2)

        self.wait(2.0)
        self.shoot("02_convert")

        self.clear_except(axes, x_name, y_name, curve, region)
        return axes, x_name, y_name, curve, region

    # ---------------------------------------------------------
    # 场景 3：如果速度不变（原结构：匀速）
    # ---------------------------------------------------------
    def part3_uniform(self, axes, x_name, y_name, curve, region):
        # 先把变速曲线收起来，换成最简单的情形
        self.play(FadeOut(curve, region), run_time=0.8)

        lead = Text(
            "如果速度是常数呢？", font=CN_FONT, font_size=30, color=FG_COLOR
        ).to_edge(UP, buff=0.8)
        self.play(FadeIn(lead), run_time=0.8)

        flat = axes.plot(
            lambda t: 5, x_range=[0, T_MAX], color=RED_WARM, stroke_width=4
        )
        self.play(Create(flat), run_time=1.0)

        box = Rectangle(
            width=axes.c2p(T_MAX, 0)[0] - axes.c2p(0, 0)[0],
            height=axes.c2p(0, 5)[1] - axes.c2p(0, 0)[1],
            color=RECT_STROKE,
            fill_color=YELLOW_WARM,
            fill_opacity=0.5,
            stroke_width=2.5,
        )
        box.move_to(axes.c2p(T_MAX / 2, 2.5))
        self.play(FadeIn(box), run_time=1.0)

        # 举例计算：底 = 时间 3 s，高 = 速度 5 m/s，面积就是路程。
        # 两个标签放进矩形内部，避开 x 轴的刻度数字。
        base_tag = Text("3 s（时间）", font=CN_FONT, font_size=24, color=FG_COLOR)
        base_tag.next_to(box.get_bottom(), UP, buff=0.22)
        height_tag = Text("5 m/s（速度）", font=CN_FONT, font_size=24, color=FG_COLOR)
        height_tag.next_to(box.get_corner(UL), DR, buff=0.55)
        self.play(FadeIn(base_tag), FadeIn(height_tag), run_time=0.8)

        formula = MathTex(
            r"S = 3\ \text{s} \times 5\ \text{m/s} = 15\ \text{m}",
            font_size=40,
            color=FG_COLOR,
        ).to_edge(DOWN, buff=0.5)
        self.play(Write(formula), run_time=1.5)

        self.wait(2.0)
        self.shoot("03_uniform")

        self.clear_except(axes, x_name, y_name, curve, region)
        return axes, x_name, y_name, curve, region

    # ---------------------------------------------------------
    # 场景 4：速度一直在变（原结构：切分）
    # ---------------------------------------------------------
    def part4_cut(self, axes, x_name, y_name, curve, region):
        lead = Text(
            "但速度不是常数，它一直在变", font=CN_FONT, font_size=30, color=FG_COLOR
        ).to_edge(UP, buff=0.8)
        self.play(FadeIn(lead), run_time=0.8)

        self.play(FadeIn(curve), FadeIn(region), run_time=1.0)

        rects = make_rects(axes, curve, dx=1)
        self.play(Create(rects), run_time=2.0)

        note = Text(
            "把 3 秒切成 3 段，每段当作匀速", font=CN_FONT, font_size=28, color=ORANGE_WARM
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=1.0)

        self.wait(2.0)
        self.shoot("04_cut")

        self.clear_except(axes, x_name, y_name, curve, region, rects)
        return axes, x_name, y_name, curve, region, rects

    # ---------------------------------------------------------
    # 场景 5：Δ 与 Σ（原结构）
    # ---------------------------------------------------------
    def part5_delta_sum(self, axes, x_name, y_name, curve, region, rects):
        # 坐标系缩小左移，给右侧公式腾出空间
        side_axes = make_axes(6.2, 4.0, SIDE_SHIFT)
        side_curve = make_curve(side_axes, stroke_width=3)
        # 阴影和矩形必须跟着坐标系一起走，否则会滞留在原地
        side_region = side_axes.get_area(
            side_curve, x_range=[0, T_MAX], color=YELLOW_LIGHT, opacity=0.5
        )
        side_rects = make_rects(side_axes, side_curve, dx=1, stroke_width=2)

        # 轴名必须跟着坐标系一起变形，否则会滞留在原地
        side_x_name = Text("t / s", font=CN_FONT, font_size=28, color=FG_COLOR)
        side_x_name.next_to(side_axes.x_axis.get_end(), DR, buff=0.15)
        side_y_name = Text("v / (m/s)", font=CN_FONT, font_size=28, color=FG_COLOR)
        side_y_name.next_to(side_axes.y_axis.get_end(), UP, buff=0.25)

        self.play(
            Transform(axes, side_axes),
            Transform(curve, side_curve),
            Transform(region, side_region),
            Transform(rects, side_rects),
            Transform(x_name, side_x_name),
            Transform(y_name, side_y_name),
            run_time=1.2,
        )

        self.play(rects[1].animate.set_fill(opacity=0.85), run_time=0.5)

        brace = Brace(Line(axes.c2p(1, 0), axes.c2p(2, 0)), DOWN, buff=0.1)
        dt_label = MathTex(r"\Delta t = 1", font_size=34, color=ORANGE_WARM)
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
            r"\Delta S_i \approx v_i \cdot \Delta t", font_size=38, color=FG_COLOR
        )
        f1.to_edge(RIGHT, buff=0.8).shift(UP * 1.6)
        self.play(Write(f1), run_time=1.0)

        self.wait(0.5)

        f2 = MathTex(
            r"S \approx \sum_{i=1}^{n} v_i \cdot \Delta t",
            font_size=42,
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
        self.shoot("05_delta_sum")

        self.clear_except(axes, x_name, y_name, curve, region, rects)
        return axes, x_name, y_name, curve, region, rects

    # ---------------------------------------------------------
    # 场景 6：左右端点夹逼
    # ---------------------------------------------------------
    def part6_squeeze(self, axes, x_name, y_name, curve, rects, region):
        # 坐标系回到居中放大
        full_axes = make_axes(7.5, 4.5, MAIN_SHIFT)
        full_curve = make_curve(full_axes)
        # 阴影与矩形同样要跟着坐标系回中，否则会滞留在左侧
        full_region = full_axes.get_area(
            full_curve, x_range=[0, T_MAX], color=YELLOW_LIGHT, opacity=0.5
        )
        full_rects = make_rects(full_axes, full_curve, dx=1)
        full_x_name = Text("t / s", font=CN_FONT, font_size=28, color=FG_COLOR)
        full_x_name.next_to(full_axes.x_axis.get_end(), DR, buff=0.15)
        full_y_name = Text("v / (m/s)", font=CN_FONT, font_size=28, color=FG_COLOR)
        full_y_name.next_to(full_axes.y_axis.get_end(), UP, buff=0.25)
        self.play(
            Transform(axes, full_axes),
            Transform(curve, full_curve),
            Transform(region, full_region),
            Transform(rects, full_rects),
            Transform(x_name, full_x_name),
            Transform(y_name, full_y_name),
            run_time=1.2,
        )

        lead = Text(
            "v = t² 单调递增", font=CN_FONT, font_size=30, color=FG_COLOR
        ).to_edge(UP, buff=0.8)
        hint = Text(
            "面积被夹在上下两条边界之间",
            font=CN_FONT,
            font_size=26,
            color=ORANGE_WARM,
        ).next_to(lead, DOWN, buff=0.3)
        self.play(FadeIn(lead), FadeIn(hint), run_time=0.8)

        # 下界：每段取左端点，矩形必然偏低
        self.play(FadeOut(rects), run_time=0.5)
        lower = make_rects(
            axes, curve, dx=1, sample="left", fill=RED_LIGHT, opacity=0.6
        )
        self.play(Create(lower), run_time=1.5)
        low_tag = Text(
            "左端点取样 → 每段都偏低", font=CN_FONT, font_size=26, color=RED_WARM
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(low_tag), run_time=0.8)

        self.wait(1.5)

        # 上界：每段取右端点，矩形必然偏高
        self.play(FadeOut(lower), FadeOut(low_tag), run_time=0.6)
        upper = make_rects(
            axes, curve, dx=1, sample="right", fill=YELLOW_WARM, opacity=0.6
        )
        self.play(Create(upper), run_time=1.5)
        high_tag = Text(
            "右端点取样 → 每段都偏高", font=CN_FONT, font_size=26, color=ORANGE_WARM
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(high_tag), run_time=0.8)

        self.wait(1.5)

        # 两个界一起摆出来
        self.play(FadeOut(upper), FadeOut(high_tag), run_time=0.6)
        self.play(Create(lower), Create(upper), run_time=1.5)

        sandwich = MathTex(r"L \;<\; S \;<\; R", font_size=44, color=FG_COLOR).to_edge(
            DOWN, buff=0.5
        )
        self.play(Write(sandwich), run_time=1.0)

        self.wait(2.0)
        self.shoot("06_squeeze")

        self.clear_except(axes, x_name, y_name, curve, region)
        return axes, x_name, y_name, curve, region

    # ---------------------------------------------------------
    # 场景 7：逼出答案
    # ---------------------------------------------------------
    def part7_answer(self, axes, x_name, y_name, curve, region):
        self.play(FadeIn(region), run_time=0.8)

        lead = Text(
            "切得越细，越接近真值", font=CN_FONT, font_size=28, color=FG_COLOR
        ).to_edge(UP, buff=0.8)
        self.play(FadeIn(lead), run_time=0.8)

        # 逐次加密矩形，右边的数值与误差同步更新
        rects = make_rects(axes, curve, dx=1)
        self.play(Create(rects), run_time=1.5)

        reading = VGroup(
            MathTex(r"S \approx 8.75", font_size=34, color=FG_COLOR),
            Text("误差 0.250", font=CN_FONT, font_size=24, color=FG_LIGHT),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).to_edge(RIGHT, buff=0.8).shift(UP * 0.7)
        self.play(FadeIn(reading), run_time=0.8)
        self.wait(0.5)

        for dx, value, err in [
            (0.5, "8.938", "0.063"),
            (0.25, "8.984", "0.016"),
            (0.1, "8.998", "0.003"),
        ]:
            new_rects = make_rects(axes, curve, dx=dx, stroke_width=1)
            new_reading = VGroup(
                MathTex(rf"S \approx {value}", font_size=34, color=FG_COLOR),
                Text(f"误差 {err}", font=CN_FONT, font_size=24, color=FG_LIGHT),
            ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(reading)
            self.play(
                ReplacementTransform(rects, new_rects),
                Transform(reading, new_reading),
                run_time=1.5,
            )
            rects = new_rects
            self.wait(0.4)

        # 上下界同时收紧，夹逼保证极限就是那个值
        self.play(FadeOut(reading), run_time=0.6)
        bound = MathTex(r"L \;<\; S \;<\; R", font_size=40, color=FG_COLOR).to_edge(
            DOWN, buff=0.5
        )
        self.play(Write(bound), run_time=1.0)

        self.play(FadeOut(lead), FadeOut(bound), run_time=0.6)

        answer = MathTex(r"S = 9", font_size=80, color=RED_WARM).to_edge(UP, buff=1.0)
        self.play(Write(answer), run_time=1.5)

        self.wait(2.0)
        self.shoot("07_answer")

        # 延伸：原函数算出的精确值，和逼近的结果对上
        extension = MathTex(
            r"\int_{0}^{3} x^{2}\,\mathrm{d}x"
            r" = \left[\frac{x^{3}}{3}\right]_{0}^{3}"
            r" = \frac{27}{3} = 9",
            font_size=36,
            color=FG_COLOR,
        ).to_edge(DOWN, buff=0.6)
        self.play(Write(extension), run_time=2.0)

        self.wait(2.5)
        self.shoot("08_exact")

        self.clear_except(axes, x_name, y_name, curve, region)

    # ---------------------------------------------------------
    # 场景 8：推广（原结构）
    # ---------------------------------------------------------
    def part8_extend(self):
        self.clear_except(run_time=0.8)

        title = Text(
            "同样的思想，不同的量", font=CN_FONT, font_size=42, color=FG_COLOR
        ).to_edge(UP, buff=0.8)
        self.play(Write(title), run_time=1.0)

        items = [
            ("速度 × 时间", "路程"),
            ("流量 × 时间", "水量"),
            ("功率 × 时间", "电能"),
        ]

        cards = VGroup()
        for top, bottom in items:
            card = RoundedRectangle(
                width=3.6,
                height=2.1,
                corner_radius=0.2,
                color=RECT_STROKE,
                stroke_width=2,
                fill_color=YELLOW_LIGHT,
                fill_opacity=0.45,
            )
            t1 = Text(top, font=CN_FONT, font_size=26, color=FG_COLOR).move_to(
                card.get_center() + UP * 0.55
            )
            t2 = Text("=", font=CN_FONT, font_size=30, color=FG_COLOR).move_to(
                card.get_center() + UP * 0.05
            )
            t3 = Text(bottom, font=CN_FONT, font_size=34, color=RED_WARM).move_to(
                card.get_center() + DOWN * 0.55
            )
            cards.add(VGroup(card, t1, t2, t3))

        cards.arrange(RIGHT, buff=0.55).shift(DOWN * 0.15)

        for card in cards:
            self.play(FadeIn(card, shift=UP * 0.3), run_time=0.7)
            self.wait(0.35)

        note = Text(
            "曲线下的面积 = 累积量", font=CN_FONT, font_size=32, color=ORANGE_WARM
        ).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(note), run_time=1.0)

        self.wait(2.0)
        self.shoot("09_extend")

        self.clear_except(run_time=0.8)

    # ---------------------------------------------------------
    # 场景 9：总结（原结构结尾）
    # ---------------------------------------------------------
    def part9_summary(self):
        k1 = Text("切碎", font=CN_FONT, font_size=60, color=RED_WARM)
        k2 = Text("近似", font=CN_FONT, font_size=60, color=ORANGE_WARM)
        k3 = Text("累加", font=CN_FONT, font_size=60, color=FG_COLOR)

        keywords = VGroup(k1, k2, k3).arrange(RIGHT, buff=1.1)
        keywords.to_edge(UP, buff=1.0)

        self.play(Write(k1), run_time=0.8)
        self.play(Write(k2), run_time=0.8)
        self.play(Write(k3), run_time=0.8)
        self.wait(1.5)

        self.play(FadeOut(keywords), run_time=0.8)

        lines = VGroup(
            Text(
                "把变化切成小段，每段近似不变，再累加。",
                font=CN_FONT,
                font_size=34,
                color=FG_COLOR,
            ),
            Text("这就是积分思想。", font=CN_FONT, font_size=34, color=ORANGE_WARM),
            Text(
                "量，可以由变化累积出来。", font=CN_FONT, font_size=28, color=FG_LIGHT
            ),
        )
        lines.arrange(DOWN, buff=0.55).to_edge(UP, buff=1.0)

        for line in lines:
            self.play(Write(line), run_time=1.1)
            self.wait(0.3)

        integral = MathTex(
            r"S = \int_0^T v(t)\,\mathrm{d}t", font_size=56, color=RED_WARM
        )
        integral.next_to(lines, DOWN, buff=1.0)
        self.play(Write(integral), run_time=1.5)

        self.wait(2.5)
        self.shoot("10_summary")