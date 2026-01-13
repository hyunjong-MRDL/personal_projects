**Markdown Language: Markup Language의 일종**

# Markdown 문법:
- Headers (헤더)
    - #으로 시작하는 text
    - #은 1~6개까지 가능
    - #이 늘어날 때 마다 제목의 스케일 축소
    - ===은 H1과 동일
    - ---은 H2와 동일

- Horizontal Rules (수평선)
    - -/*/_을 3개 이상 작성

- Line Breaks (줄바꿈)
    - \<br\>를 활용해서 줄바꿈 가능

- Emphasis (강조)
    1. Italic: */_로 감싼 텍스트
    2. Bold: **/__로 감싼 텍스트
    3. 취소선: ~~로 감싼 텍스트

- Block quotes (인용)
    - \>으로 시작하는 text
    - \>는 3개까지 가능

- Lists (목록)
    1. Unordered lists
        - */+/-를 이용해서 순서가 없는 목록을 만들 수 있다
        - 들여쓰기(indent)를 하면 모양이 바뀐다
    2. Ordered lists
        - 숫자를 기입하면 순서가 있는 목록이 된다
        - 들여쓰기를 하면 모양이 바뀐다

- Backslash Escapes
    - 특수문자를 표현하고자 할 때, 표시될 문자 앞에 \를 붙인다

- Images
    - Link와 비슷하지만, 앞에 !가 붙는다
    1. Inline-image: \!\[alt_text\]\(/test.png\)
    2. Link-image:   \!\[alt_text\]\(/image_URL\)
    - 이미지 크기 변경: \<img width="___px" height="___px"\>\</img\>

- Links (Anchor)
    1. 외부 링크: \[display_name\]\(link_URL\)
    2. 내부(hash) 링크: \[display_name\]\(#header-to-be-linked\)

- Code Block
    - 간단한 inline-code는 text의 앞뒤를 '기호로 감싸면 된다
    - ''' 혹은 ~~~ 코드
    - 코드가 여러 줄인 경우, 줄 앞에 indent를 추가하면 된다
    - '''옆에 언어 지정 가능

- Check List
    - 줄 앞에 -[]를 써서 미완료된 리스트 표시
    - 줄 앞에 - [x]를 써서 완료된 리스트 표시

- Table
    - Header와 Cell을 구분할 때 3개 이상의 - 기호 필요
    - Header cell을 구분하면서 : 기호로 셀 내용 정렬 가능
    - 가장 좌/우측에 있는 | 기호는 생략 가능