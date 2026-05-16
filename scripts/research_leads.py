#!/usr/bin/env python3
"""
Daily NINE lead researcher.
Picks a city based on today's date, calls Claude API to research local service
businesses with weak web presence, and writes the leads file.
"""

import anthropic
import datetime
import os
import sys

CITIES = [
    "Los Angeles, CA",
    "Chicago, IL",
    "Houston, TX",
    "Phoenix, AZ",
    "Philadelphia, PA",
    "San Antonio, TX",
    "San Diego, CA",
    "Dallas, TX",
    "Jacksonville, FL",
    "Austin, TX",
    "Columbus, OH",
    "Charlotte, NC",
    "Indianapolis, IN",
    "San Francisco, CA",
    "Seattle, WA",
    "Denver, CO",
    "Nashville, TN",
    "Oklahoma City, OK",
    "El Paso, TX",
    "Portland, OR",
    "Las Vegas, NV",
    "Memphis, TN",
    "Louisville, KY",
    "Baltimore, MD",
    "Milwaukee, WI",
    "Albuquerque, NM",
    "Tucson, AZ",
    "Fresno, CA",
    "Sacramento, CA",
    "Mesa, AZ",
    "Atlanta, GA",
    "Miami, FL",
    "Minneapolis, MN",
    "New Orleans, LA",
    "Cleveland, OH",
    "Tampa, FL",
    "Pittsburgh, PA",
    "Raleigh, NC",
    "Kansas City, MO",
    "Virginia Beach, VA",
    "Omaha, NE",
    "Colorado Springs, CO",
    "Long Beach, CA",
    "Bakersfield, CA",
    "Aurora, CO",
    "Honolulu, HI",
    "Anaheim, CA",
    "Santa Ana, CA",
    "Corpus Christi, TX",
    "Riverside, CA",
]

PROMPT_TEMPLATE = """You are a lead researcher for NINE, a web design and digital marketing agency.

Research local service businesses in {city} that are likely to have outdated or poor websites
and would benefit from NINE's services (web redesign, online booking integration, SEO, Google Ads setup).

Target niches: restaurants, gyms/fitness studios, nail/hair salons, spas, local retail shops.
Qualifier: outdated website, no online booking, no clear SEO presence, Wix/Squarespace template sites.

For each lead, find:
- Business name
- Address
- Phone number
- Email (if publicly available)
- Website URL
- What's wrong with their web presence (specific pitch angle)

Compile 15–20 qualified leads. Group by category (Gyms, Restaurants, Salons, Other).
For each, write one line on the specific pitch NINE should use.

Also include:
1. A ready-to-send email template tailored to this city
2. A prioritized send order (best leads first based on email availability and pitch strength)

Format the output as clean markdown, ready to save as a leads file.
Start with: # {city} Outreach Leads — {date}
"""


def pick_city(date: datetime.date) -> str:
    day_index = date.toordinal() % len(CITIES)
    return CITIES[day_index]


def research_leads(city: str, date: datetime.date) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = PROMPT_TEMPLATE.format(
        city=city,
        date=date.strftime("%B %d, %Y"),
    )

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        system=(
            "You are a sharp lead researcher for a web agency called NINE. "
            "You produce concise, actionable lead lists — no filler, no disclaimers. "
            "Research real business types and realistic contact patterns for the given city. "
            "Be specific about web weaknesses and pitch angles."
        ),
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def main():
    today = datetime.date.today()
    city = pick_city(today)

    print(f"Researching leads in: {city}", file=sys.stderr)

    content = research_leads(city, today)

    city_slug = city.split(",")[0].lower().replace(" ", "-")
    filename = f"outreach/leads-{city_slug}-{today.isoformat()}.md"

    os.makedirs("outreach", exist_ok=True)
    with open(filename, "w") as f:
        f.write(content)

    print(f"Saved: {filename}", file=sys.stderr)
    print(filename)  # stdout for the workflow to capture


if __name__ == "__main__":
    main()
