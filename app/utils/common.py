import re
import logging
from typing import Dict, Tuple

from app.error.chat_exception import QuizParsingException

logger = logging.getLogger(__name__)


# 퀴즈 응답 추출
def parse_quiz_content(quiz_content: str) -> Dict[str, any]:
    try:
        # 줄 바꿈 기준으로 텍스트 나눔
        lines = quiz_content.strip().split("\n")

        # 퀴즈 문제 추출
        question = lines[0].strip()
        logger.info(f"추출된 문제: {question}")

        # 선택지 추출
        options = []
        for line in lines[1:]:
            # 예시) "1번. 근정전" -> "근정전" 추출
            match = re.match(r"^\d+번\.\s*(.+)$", line.strip())
            if match:
                options.append(match.group(1))
            if len(options) == 5:
                break

        logger.info(f"추출된 선택지: {options}")

        if len(options) < 2:
            raise ValueError("최소 2개 이상의 선택지가 필요합니다.")

        # 정답 추출
        answer_match = re.search(
            r"정답\s*:?\s*(\d+)(번)?", quiz_content, re.IGNORECASE
        )
        if answer_match:
            answer = answer_match.group(1)
            if int(answer) > len(options):
                raise QuizParsingException(
                    f"정답 번호({answer})가 선택지 개수({len(options)})를 초과합니다."
                )
            logger.info(f"추출된 정답 값 : {answer}")
        else:
            # 정답을 찾지 못한 경우, '정답'이라는 단어 뒤의 첫 번째 숫자를 찾습니다.
            fallback_answer_match = re.search(
                r"정답.*?(\d+)", quiz_content, re.IGNORECASE | re.DOTALL
            )
            if fallback_answer_match:
                answer = fallback_answer_match.group(1)
                logger.info(f"대체 방법으로 추출된 정답 값 : {answer}")
            else:
                raise QuizParsingException("정답 값을 추출할 수 없습니다.")

        # 설명 추출
        explanation_match = re.search(
            r"해설\s*:?\s*(.+)$", quiz_content, re.IGNORECASE | re.DOTALL
        )
        if explanation_match:
            explanation = explanation_match.group(1).strip()
            logger.info(f"추출된 설명: {explanation}")
        else:
            # '설명:' 이후의 모든 텍스트를 설명으로 간주
            explanation_parts = quiz_content.split("설명", 1)
            if len(explanation_parts) > 1:
                explanation = explanation_parts[1].strip()
                logger.info(f"대체 방법으로 추출된 설명: {explanation}")
            else:
                raise QuizParsingException("설명을 찾을 수 없습니다.")

        parsed_quiz = {
            "question": question,
            "options": options,
            "answer": answer,
            "explanation": explanation,
        }

        # 최종 유효성 검사
        if not all(
            [
                parsed_quiz["question"],
                parsed_quiz["options"],
                parsed_quiz["answer"],
                parsed_quiz["explanation"],
            ]
        ):
            raise QuizParsingException("퀴즈의 필수 요소가 누락되었습니다.")

        logger.info(f"성공적으로 파싱된 퀴즈: {parsed_quiz}")

        return parsed_quiz

    except QuizParsingException as e:
        logger.error(f"퀴즈 내용 파싱 중 오류 발생: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"퀴즈 내용 파싱 중 오류 발생: {str(e)}")
        raise ValueError("퀴즈 내용을 파싱할 수 없습니다.") from e


# 문화재 조회 location 파싱
def parse_location_for_detail(location: str) -> str:
    if not location:
        return ""

    # 불필요한 공백, 탭, 줄바꿈 제거
    cleaned = re.sub(r"\s+", " ", location).strip()

    # '/' 기호 기준으로 분리하고 첫번째 부분만 사용
    parts = cleaned.split("/")
    if len(parts) > 1:
        cleaned = parts[0].strip()

    # '(' 이후 내용 제거 (지번, 정보 등)
    cleaned = re.sub(r"\(.*?\)", "", cleaned).strip()

    return cleaned


# 문화재 리스트 location 파싱
def parse_location_for_list(location: str) -> str:
    if not location:
        return ""

    # 불필요한 공백, 탭, 줄바꿈 제거
    cleaned = re.sub(r"\s+", " ", location).strip()

    # '/' 기호 기준으로 분리하고 첫번째 부분만 사용
    parts = cleaned.split("/")
    if len(parts) > 1:
        cleaned = parts[0].strip()

    # 괄호와 그 내용 제거
    cleaned = re.sub(r"\(.*?\)", "", cleaned).strip()

    # 쉼표 이후 내용 제거
    cleaned = cleaned.split(",")[0].strip()

    # 도로명 주소 처리
    road_address = re.match(r"^(.+[시군구])\s+(.+[로길])", cleaned)
    if road_address:
        cleaned = road_address.group(0)
    else:
        # 특정 키워드 이후 내용 제거
        keywords = ["가", "동", "읍", "면"]
        for keyword in keywords:
            match = re.search(f"{keyword}\\s", cleaned)
            if match:
                end_index = match.end()
                cleaned = cleaned[:end_index].strip()
                break

    # 숫자로 끝나는 경우, 숫자 그 앞 공백 제거
    cleaned = re.sub(r"\s+\d+$", "", cleaned)

    return cleaned


# 문화재 사용자 거리 파싱
def parse_heritage_dist_range(distance_range: str) -> Tuple[float, float]:
    ranges = {
        "0-0.5": (0, 0.5),
        "0.5-1": (0.5, 1),
        "1-10": (1, 10),
        "10-100": (10, 100),
        "100-1000": (100, 1000),
    }

    return ranges.get(distance_range, (0, float("inf")))


# 해시태그 처리 함수
def process_hashtags(text):
    hashtags = []
    current_tag = ""
    for word in text.split():
        if word.startswith("#"):
            if current_tag:
                hashtags.append(current_tag.strip())
            current_tag = word
        elif current_tag:
            current_tag += " " + word
        else:
            continue
    if current_tag:
        hashtags.append(current_tag.strip())
    return hashtags


def extract_hashtags(text):
    # 해시태그를 추출하고 공백을 제거합니다.
    hashtags = re.findall(r"#\s*([^#\n]+)", text)

    # 각 해시태그의 앞뒤 공백을 제거하고 내부 공백을 제거합니다.
    cleaned_hashtags = ["#" + "".join(tag.split()) for tag in hashtags]

    # 중복 제거 및 정렬
    unique_hashtags = sorted(set(cleaned_hashtags))

    return unique_hashtags
