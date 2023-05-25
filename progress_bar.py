class ProgressBar:
    bar_string_fmt = "\rProgress: [{}{}] {:.2%} {}/{}"
    cnt = 0

    def __init__(self, total, bar_total=20):
        # task 的總數
        self.total = total

        # progress bar 的長度，可依個人喜好設定
        self.bar_total = bar_total

    def update(self, step=1):
        # 更新 progress bar 的進度

        total = self.total
        self.cnt += step

        # bar 的數量
        bar_cnt = (int((self.cnt/total)*self.bar_total))
        # 空白的數量
        space_cnt = self.bar_total - bar_cnt

        # 顯示 progress bar
        progress = self.bar_string_fmt.format(
            "█" * bar_cnt,
            " " * space_cnt,
            self.cnt/total,
            self.cnt,
            total
        )

        print(progress, end="")

        percent = self.cnt/total
        # 100%
        if percent == 1:
            print("\n")
        elif percent >= 1:
            print("")