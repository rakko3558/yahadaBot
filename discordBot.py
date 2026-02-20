import discord 
import os
import random
import json
from discord.ext import commands
from keep_alive import keep_alive
import re # 記得在程式最上方加上 import re
from Asakusa import all_sticks
    # 使用正則表達式尋找 數字d數字 (例如 3d100)

# 1. 設定 Intents 與 前綴 (這裡我改成 . 你可以隨意換成喜歡的符號)
intents = discord.Intents.all() 
bot = commands.Bot(command_prefix="!", intents=intents)
#with open('token.json', "r", encoding = "utf8") as file:
#    TOKEN = json.load(file)

# --- 事件處理 ---


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="偷吃賊 現行犯 趕老鼠"))
    print(f'機器人已上線：{bot.user}')


  

@bot.event
async def on_message(message):
    # 1. 排除機器人自己的訊息
    if message.author == bot.user:
        return

    # 2. 檢查訊息是否以 cc 開頭 (不論有沒有空格)
    if message.content.startswith("cc"):
        # 移除 "cc" 兩個字
        raw_content = message.content[2:].strip()
        
        try:
            # 拆分數字和動作 (例如 "50 閃避" -> ["50", "閃避"])
            parts = raw_content.split(maxsplit=1)
            if not parts:
                return # 只有打 cc 沒打數字就不理會
                
            target_value = int(parts[0])
            goal = parts[1] if len(parts) > 1 else ""

            # --- 骰子邏輯 ---
            roll = random.randint(1, 100)
            extreme_cutoff = target_value // 5
            hard_cutoff = target_value // 2
            
            if roll == 1:
                status = "【大成功】"
            elif roll == 100:
                status = "【大失敗】"
            elif roll <= extreme_cutoff:
                status = "【極限成功】"
            elif roll <= hard_cutoff:
                status = "【困難成功】"
            elif roll <= target_value:
                status = "【一般成功】"
            else:
                status = "【失敗】"

            # 組合回覆訊息
            response = (
                f"{message.author.mention}\n"
                f"1D100 ≤ {target_value}\n"
                f"{roll} → {status} : {goal}"
            )
            await message.channel.send(response)

        except ValueError:
            # 如果 cc 後面接的不是數字 (例如打 cctest)
            await message.channel.send("格式錯誤！請輸入 `cc數字 動作` (例如：`cc50 偵察`)")

    # 3. 檢查訊息是否以 "隨機" 開頭
    elif message.content.startswith("隨機"):
        # 移除 "隨機" 兩個字並去空白
        raw_content = message.content[2:].strip()
        
        if not raw_content:
            return

        # 將選項拆開 (預設用空格拆分)
        options = raw_content.split()

        if len(options) < 2:
            return
            
        if len(options) > 100:
            await message.channel.send("太多了 不要吵")
            return

        # 隨機選出一個
        choice = random.choice(options)

        # 組合回覆訊息
        # " ".join(options) 會把列表變回 a b c d e 的格式
        response = (
            f"{message.author.mention}\n"
            f"隨機 [ {' '.join(options)} ]\n"
            f"→ **{choice}**"
        )
        await message.channel.send(response)
    elif (re.match(r'^(\d+)[dD](\d+)$', message.content.strip())):
        match = re.match(r'^(\d+)[dD](\d+)$', message.content.strip())
        num_dice = int(match.group(1))  # 骰子顆數
        die_sides = int(match.group(2)) # 骰子面數

        # 限制一下數量，避免被惡意洗版
        if num_dice > 100 or num_dice<=0 :
            await message.channel.send("骰子顆數請在 1~100 之間")
            return
        if die_sides <= 0 or die_sides > 1000:
            await message.channel.send("骰子面數請在 1~1000 之間")
            return

        # 擲骰子
        rolls = [random.randint(1, die_sides) for _ in range(num_dice)]
        total = sum(rolls)

        # 組合過程字串 (例如 "3+5+2")
        # 如果只有一顆骰子，就不需要顯示加號過程
        if num_dice > 1:
            process = "+".join(map(str, rolls))
            response = (
                f"{message.author.mention}\n"
                f"{num_dice}d{die_sides}：\n"
                f"[{process}] = **{total}**"
            )
        else:
            response = (
                f"{message.author.mention}\n"
                f"1d{die_sides}：**{total}**"
            )
            
        await message.channel.send(response)

    elif message.content.startswith("問神"):
        # 抓取祈求事項
        reason = message.content[2:].strip()
        if not reason:
            await message.channel.send("請輸入你想祈求的事項，例如：`問神 今天的面試`")
            return

        # 隨機抽取一支籤
        stick = random.choice(all_sticks)

        # 格式化輸出
        response = (
            f"{message.author.mention} 針對「{reason}」的求籤結果：\n\n"
            f"**[{stick['type']}]** {stick['poem']}\n"
            f"----------------------------------\n"
            f"{stick['explain']}\n"
            f"----------------------------------\n"
            f"{stick['result']}\n\n"
            f"建議：{stick['note']}"
        )
        
        await message.channel.send(response)
    # 必須加上這行，否則其他的 @bot.command (如 hello) 會失效
    await bot.process_commands(message)

# --- 其他原本的指令 ---
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hi {ctx.author.mention}!")

#bot.run(TOKEN['token'])

try:
  TOKEN = os.getenv("TOKEN") or ""
  if TOKEN == "":
    raise Exception("Please add your token to the Secrets pane.")
  keep_alive()
  bot.run(TOKEN)
except discord.HTTPException as e:
    if e.status == 429:
        print(
            "The Discord servers denied the connection for making too many requests"
        )
        print(
            "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
        )
    else:
        raise e