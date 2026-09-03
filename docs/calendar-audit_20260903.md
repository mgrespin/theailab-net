# Calendar consistency audit — 2026-09-03 (T-11)

Cross-checked every date on `core/schedule.html`, `core/syllabus.html`,
`core/assignments.html`, and all 15 `weeks/week-NN.html` pages against each
other and against the actual 2026 calendar.

## Result: internally consistent

- Every week page's stated session date falls on the weekday it names
  (Tuesday / Thursday) for 2026.
- Week 1 (Thu Aug 27 only) and Week 7 (Tue Oct 6 only) correctly reflect the
  single-session weeks around the term start and October Break.
- No week session lands inside October Break (Oct 8–9) or the Thanksgiving
  recess (Nov 21–29). Week 13 (Nov 17/19) → Week 14 (Dec 1/3) correctly skips
  Thanksgiving week.
- Week 15 (Dec 8/10) sits before the last day of classes (Fri Dec 11); finals
  Dec 14–18.
- Mini-project due dates agree between the Syllabus weights table and the
  Assignments page (MP1 Sep 4, MP2 Sep 25, MP3 Oct 23, MP4 Nov 20); MP4
  presentation dates (Nov 17/19) match Week 13.

`tests/test_integration_links.py::TestCalendarConsistency` now guards these
relationships.

## To verify against the official Kenyon 2026–27 academic calendar

The pages assert these key dates; they are internally consistent but were not
checked against the registrar's calendar in this pass:

- Classes begin Thu Aug 27; October Break Thu–Fri Oct 8–9.
- Thanksgiving recess Sat Nov 21 – Sun Nov 29 (i.e. no class the full week of
  Nov 23–27).
- Last day of classes Fri Dec 11; final exam period Mon–Fri Dec 14–18;
  semester ends 4:30 PM Fri Dec 18.

If any of these differ from the official calendar, update `core/schedule.html`
first (it is the stated source of truth) and the affected week pages.
