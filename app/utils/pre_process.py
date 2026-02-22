import asyncio
import re
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import async_session, init_db
from app.models import Document, DocumentStatus, ScriptLine, Speaker

DATA_DIR = Path(__file__).parents[2] / "data"
CATEGORY_ID = 1


def parse_filename(filepath: Path) -> tuple[str, str]:
    parts = filepath.stem.split("_")
    return parts[-2], parts[-1]  # recorded_date, recorded_time


def parse_txt(filepath: Path) -> list[dict]:
    content = filepath.read_text(encoding="utf-8-sig")  # BOM 제거
    lines = content.splitlines()[3:]  # 첫 3줄 스킵 (제목, 날짜정보, 빈줄)

    pattern = re.compile(r"^(.+?)\s+(\d{1,2}:\d{2})\s*$")

    result = []
    current_speaker = None
    current_time = None
    current_text_lines = []

    for line in lines:
        match = pattern.match(line)
        if match:
            if current_speaker and current_text_lines:
                result.append(
                    {
                        "speaker": current_speaker,
                        "start_time": current_time,
                        "text": " ".join(current_text_lines).strip(),
                    }
                )
            current_speaker = match.group(1).strip()
            current_time = match.group(2).strip()
            current_text_lines = []
        elif line.strip():
            current_text_lines.append(line.strip())

    # Loop에서 제외된 마지막 줄 처리
    if current_speaker and current_text_lines:
        result.append(
            {
                "speaker": current_speaker,
                "start_time": current_time,
                "text": " ".join(current_text_lines).strip(),
            }
        )

    return result


async def process_file(session: AsyncSession, txt_path: Path):
    recorded_date, recorded_time = parse_filename(txt_path)

    m4a_files = list(DATA_DIR.glob(f"*_{recorded_date}_{recorded_time}*.m4a"))
    audio_url = m4a_files[0].name if m4a_files else None
    file_size = m4a_files[0].stat().st_size if m4a_files else None
    print(file_size)

    document = Document(
        category_id=CATEGORY_ID,
        title=txt_path.name,
        recorded_date=recorded_date,
        recorded_time=recorded_time,
        audio_url=audio_url,
        file_size=file_size,
        status=DocumentStatus.PENDING,
    )
    session.add(document)
    await session.flush()

    lines = parse_txt(txt_path)

    speaker_map = {}
    for name in dict.fromkeys(l["speaker"] for l in lines):
        spk = Speaker(document_id=document.id, name=name)
        session.add(spk)
        await session.flush()
        speaker_map[name] = spk.id

    for order, line in enumerate(lines):
        session.add(
            ScriptLine(
                document_id=document.id,
                speaker_id=speaker_map[line["speaker"]],
                text=line["text"],
                start_time=line["start_time"],
                order=order,
            )
        )

    await session.commit()


async def main():
    await init_db()
    async with async_session() as session:
        for txt_path in DATA_DIR.glob("*.txt"):
            await process_file(session, txt_path)


if __name__ == "__main__":
    asyncio.run(main())
