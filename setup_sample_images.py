"""
Generate crisp, professional demo images for seeded complaints in static/uploads
"""
import os
from PIL import Image, ImageDraw, ImageFont

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

SAMPLES = [
    {
        "filename": "pothole_ward12.jpg",
        "title": "Severe Pothole Cluster",
        "subtitle": "Ward 12, Ring Road - Depth: ~14cm",
        "bg_color": (55, 65, 81),
        "accent": (239, 68, 68),
        "icon_label": "POTHOLE"
    },
    {
        "filename": "garbage_ward7.jpg",
        "title": "Overflowing Garbage Dump",
        "subtitle": "Ward 7, Near Community Center",
        "bg_color": (78, 60, 45),
        "accent": (245, 158, 11),
        "icon_label": "SOLID WASTE"
    },
    {
        "filename": "streetlight_ward4.jpg",
        "title": "Non-Functional Streetlight Pole",
        "subtitle": "Ward 4, West End Avenue #22",
        "bg_color": (30, 41, 59),
        "accent": (251, 191, 36),
        "icon_label": "STREETLIGHT"
    },
    {
        "filename": "water_leak_civillines.jpg",
        "title": "Underground Pipeline Rupture",
        "subtitle": "Civil Lines, Near High Court Gate",
        "bg_color": (30, 58, 138),
        "accent": (56, 189, 248),
        "icon_label": "WATER LEAK"
    },
    {
        "filename": "road_damage_sadar.jpg",
        "title": "Asphalt Caving & Heavy Cracking",
        "subtitle": "Sadar Bazaar Market Road",
        "bg_color": (75, 85, 99),
        "accent": (249, 115, 22),
        "icon_label": "ROAD DAMAGE"
    },
    {
        "filename": "drain_manishnagar.jpg",
        "title": "Choked Stormwater Drain",
        "subtitle": "Manish Nagar Railway Crossing Road",
        "bg_color": (41, 37, 36),
        "accent": (220, 38, 38),
        "icon_label": "DRAINAGE"
    },
    {
        "filename": "pothole_dharampeth.jpg",
        "title": "Dangerous Pothole on Curve",
        "subtitle": "Dharampeth Main Commercial Street",
        "bg_color": (51, 65, 85),
        "accent": (239, 68, 68),
        "icon_label": "POTHOLE"
    },
    {
        "filename": "waste_ramdaspeth.jpg",
        "title": "Illegal Construction Debris",
        "subtitle": "Ramdaspeth Canal Road",
        "bg_color": (68, 64, 60),
        "accent": (234, 179, 8),
        "icon_label": "DEBRIS"
    }
]

def create_sample_images():
    for item in SAMPLES:
        path = os.path.join(UPLOAD_DIR, item["filename"])
        if os.path.exists(path):
            continue
        
        # 640x400 banner
        img = Image.new("RGB", (640, 400), color=item["bg_color"])
        draw = ImageDraw.Draw(img)
        
        # Draw background pattern/grid
        for x in range(0, 640, 40):
            draw.line([(x, 0), (x, 400)], fill=(item["bg_color"][0] + 10, item["bg_color"][1] + 10, item["bg_color"][2] + 10), width=1)
        for y in range(0, 400, 40):
            draw.line([(0, y), (640, y)], fill=(item["bg_color"][0] + 10, item["bg_color"][1] + 10, item["bg_color"][2] + 10), width=1)
        
        # Draw accent banner header
        draw.rectangle([(0, 0), (640, 8)], fill=item["accent"])
        
        # Draw a civic badge rectangle
        draw.rounded_rectangle([(40, 40), (220, 80)], radius=6, fill=item["accent"])
        draw.text((55, 52), item["icon_label"], fill=(255, 255, 255))
        
        # Draw title and subtitle
        draw.text((40, 130), item["title"], fill=(255, 255, 255))
        draw.text((40, 180), item["subtitle"], fill=(203, 213, 225))
        
        # Draw geotag simulation box
        draw.rounded_rectangle([(40, 260), (600, 350)], radius=8, fill=(15, 23, 42))
        draw.text((60, 275), "Civisense - Verified Citizen Geo-Evidence Capture", fill=(148, 163, 184))
        draw.text((60, 305), f"Status: Auto-Indexed | Nagpur Municipal Corporation Ward Region", fill=(52, 211, 153))

        img.save(path, "JPEG", quality=90)
        print(f"Created {item['filename']}")

if __name__ == "__main__":
    create_sample_images()
