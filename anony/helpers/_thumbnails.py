# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import os
import asyncio
import aiohttp
from PIL import (Image, ImageDraw, ImageEnhance,
                 ImageFilter, ImageFont)

from anony import config
from anony.helpers import Media, Track


class Thumbnail:
    def __init__(self):
        try:
            self.font_title = ImageFont.truetype("anony/helpers/Raleway-Bold.ttf", 40)
            self.font_artist = ImageFont.truetype("anony/helpers/Inter-Light.ttf", 30)
            self.font_time = ImageFont.truetype("anony/helpers/Inter-Light.ttf", 22)
        except:
            self.font_title = ImageFont.load_default()
            self.font_artist = ImageFont.load_default()
            self.font_time = ImageFont.load_default()

    def _make_sq(self, im, radius=80):
        """Creates a rounded square image."""
        mask = Image.new('L', im.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0) + im.size, radius=radius, fill=255)
        out = Image.new('RGBA', im.size, (0, 0, 0, 0))
        out.paste(im, (0, 0), mask)
        return out

    def _draw_player(self, thumb_path, videoid, title, duration, artist):
        # 1. Background
        if thumb_path and os.path.exists(thumb_path):
            background = Image.open(thumb_path)
        else:
            background = Image.new("RGB", (1280, 720), (20, 20, 20))

        background = background.resize((1280, 720))
        background = background.filter(ImageFilter.GaussianBlur(radius=60))

        # Darken background
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.3)

        draw = ImageDraw.Draw(background)

        # 2. Thumbnail image (Left)
        if thumb_path and os.path.exists(thumb_path):
            thumb = Image.open(thumb_path).convert("RGBA")
        else:
            thumb = Image.new("RGBA", (520, 520), (40, 40, 40, 255))

        thumb = thumb.resize((520, 520))
        thumb = self._make_sq(thumb, radius=80)
        background.paste(thumb, (90, 100), thumb)

        # 3. Text (Title & Artist)
        x_start = 720
        x_end = 1210

        # Max widths
        max_title_width = 350

        title = str(title)
        if draw.textbbox((0, 0), title, font=self.font_title)[2] > max_title_width:
            while draw.textbbox((0, 0), title + "...", font=self.font_title)[2] > max_title_width:
                title = title[:-1]
            title += "..."

        artist = str(artist)
        if draw.textbbox((0, 0), artist, font=self.font_artist)[2] > max_title_width:
            while draw.textbbox((0, 0), artist + "...", font=self.font_artist)[2] > max_title_width:
                artist = artist[:-1]
            artist += "..."

        draw.text((x_start, 160), title, font=self.font_title, fill="white")
        draw.text((x_start, 215), artist, font=self.font_artist, fill=(180, 180, 180))

        # Star and Dots icons
        draw.ellipse([1100, 160, 1150, 210], fill=(255, 255, 255, 30))
        star_pts = [
            (1125, 172), (1128, 182), (1138, 182), (1130, 189),
            (1134, 199), (1125, 193), (1116, 199), (1120, 189),
            (1112, 182), (1122, 182)
        ]
        draw.polygon(star_pts, fill="white")

        draw.ellipse([1170, 160, 1220, 210], fill=(255, 255, 255, 30))
        for y in [175, 185, 195]:
            draw.ellipse([1192, y, 1198, y+6], fill="white")

        # 4. Progress Bar
        bar_y = 300
        progress = 0.1 # Dummy progress
        draw.line([x_start, bar_y, x_end, bar_y], fill=(100, 100, 100), width=10)
        current_x = x_start + (x_end - x_start) * progress
        draw.line([x_start, bar_y, current_x, bar_y], fill=(220, 220, 220), width=10)
        draw.ellipse([current_x - 10, bar_y - 10, current_x + 10, bar_y + 10], fill=(220, 220, 220))

        # 5. Time Labels
        draw.text((x_start, 330), "0:03", font=self.font_time, fill=(180, 180, 180))
        draw.text((x_end - 60, 330), f"-{duration}", font=self.font_time, fill=(180, 180, 180))

        # 6. Controls
        y_ctrl = 520
        # Skip Back
        draw.polygon([(820, y_ctrl), (770, y_ctrl - 25), (820, y_ctrl - 50)], fill="white")
        draw.polygon([(770, y_ctrl), (720, y_ctrl - 25), (770, y_ctrl - 50)], fill="white")

        # Play/Pause
        draw.rounded_rectangle([930, y_ctrl - 60, 950, y_ctrl + 10], radius=5, fill="white")
        draw.rounded_rectangle([970, y_ctrl - 60, 990, y_ctrl + 10], radius=5, fill="white")

        # Skip Forward
        draw.polygon([(1100, y_ctrl), (1150, y_ctrl - 25), (1100, y_ctrl - 50)], fill="white")
        draw.polygon([(1150, y_ctrl), (1200, y_ctrl - 25), (1150, y_ctrl - 50)], fill="white")

        # 7. Volume Bar
        y_vol = 630
        draw.line([x_start + 30, y_vol, x_end - 30, y_vol], fill=(100, 100, 100), width=8)
        # Dummy volume 70%
        draw.line([x_start + 30, y_vol, x_start + 30 + (x_end - x_start - 60) * 0.7, y_vol], fill="white", width=8)
        draw.ellipse([x_start + 30 + (x_end - x_start - 60) * 0.7 - 8, y_vol - 8, x_start + 30 + (x_end - x_start - 60) * 0.7 + 8, y_vol + 8], fill="white")

        # Speaker icons
        # Left
        draw.polygon([(x_start, y_vol), (x_start + 10, y_vol - 8), (x_start + 10, y_vol + 8)], fill="white")
        draw.rectangle([x_start - 10, y_vol - 5, x_start, y_vol + 5], fill="white")
        # Right
        draw.polygon([(x_end - 10, y_vol), (x_end, y_vol - 8), (x_end, y_vol + 8)], fill="white")
        draw.rectangle([x_end - 20, y_vol - 5, x_end - 10, y_vol + 5], fill="white")
        draw.arc([x_end + 2, y_vol - 8, x_end + 15, y_vol + 8], start=-60, end=60, fill="white", width=2)
        draw.arc([x_end - 2, y_vol - 12, x_end + 20, y_vol + 12], start=-60, end=60, fill="white", width=2)

        # 8. Bottom Icons
        y_bottom = 690
        # Quote bubble icon
        draw.rounded_rectangle([800, y_bottom, 835, y_bottom + 25], radius=5, outline="white", width=2)
        # draw a small "99" inside
        try:
            qfont = ImageFont.truetype("anony/helpers/Inter-Light.ttf", 15)
        except:
            qfont = ImageFont.load_default()
        draw.text((809, y_bottom + 2), "99", font=qfont, fill="white")

        # List icon
        for i in range(3):
            draw.line([1110, y_bottom + 5 + i*8, 1140, y_bottom + 5 + i*8], fill="white", width=3)
            draw.ellipse([1100, y_bottom + 3 + i*8, 1104, y_bottom + 7 + i*8], fill="white")

        final_thumb = background.convert("RGB")
        out_path = f"cache/{videoid}.png"
        final_thumb.save(out_path)
        return out_path

    async def generate(self, media: Media | Track) -> str:
        try:
            videoid = media.id
            output = f"cache/{videoid}.png"
            if os.path.exists(output):
                return output

            title = media.title
            duration = media.duration
            artist = getattr(media, "channel_name", "Unknown Artist") or "Unknown Artist"
            thumbnail_url = getattr(media, "thumbnail", None)

            thumb_path = f"cache/thumb_{videoid}.png"

            if not os.path.exists(thumb_path) and thumbnail_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(thumbnail_url) as resp:
                        if resp.status == 200:
                            with open(thumb_path, "wb") as f:
                                f.write(await resp.read())

            if not os.path.exists(thumb_path):
                thumb_path = None

            return await asyncio.to_thread(
                self._draw_player, thumb_path, videoid, title, duration, artist
            )
        except Exception:
            return config.DEFAULT_THUMB
