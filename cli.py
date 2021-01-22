from configparser import ConfigParser
from random import choice
from astr.command import execute


def _GET_FAREWELL() -> str: return choice([  # pylint: disable=invalid-name,multiple-statements
    '再会！', '感谢使用！', '感谢支持！',
    '如有疑问请反馈到：https://github.com/urain39/astr-archives',
])


def main() -> None:
    cfg = ConfigParser()
    cfg.read('astr.ini', encoding='utf-8')

    while True:
        cmd = input('> ')

        if cmd in ('e', 'exit', 'q', 'quit'):
            break

        if cmd in ('r', 'reload'):
            cfg.read('astr.ini', encoding='utf-8')
            print("已重载配置文件。")

            continue

        if cmd not in ('x', 'extract', 'i', 'inject', 'u', 'update'):
            print(
                '工具设计与实现由 RustyV 完成，最后修改时间是2021年1月22日。\n'
                '\n'
                '目前支持的命令有：\n'
                '    x, extract   提取源码中的字符串。\n'
                '    i, inject    将翻译后的字符串注入到源码中。\n'
                '    u, update    更新数据库中翻译后字符串的更改时间。\n'
                '\n'
                '交互式工具额外扩展的命令有：\n'
                '   e, exit       退出交互式界面。\n'
                '   q, quit       e, exit 的别名。\n'
                '   r, reload     重新加载配置文件。\n'
                '\n'
                '注意: 请勿随意使用 "u, update" 选项，该选项可能会造成不必要的错误。\n'
            )

        try:
            execute(cmd, cfg)
        # pylint: disable=broad-except
        except Exception as e:
            print(e)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

    print(_GET_FAREWELL())
