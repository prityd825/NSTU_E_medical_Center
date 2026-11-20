# NSTU E-Medical Center

An online home for the medical center at **Noakhali Science and Technology University**.
Students, teachers and staff can book a visit, chat with a doctor and download their prescriptions,
while the center keeps track of patients, appointments and medicine stock in one place.

We built it because the paper-and-queue system wasted everyone's time. Now most things can be done from a phone.

**Live demo:** https://nstu-emedical.onrender.com
(it runs on Render's free plan, so the first visit after a quiet spell can take up to a minute to wake up)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/prityd825/NSTU_E_medical_Center)

---

## Try it with a demo account

Every demo account uses the same password: **`Demo@1234`**

| Role | Username | Sign in at | What you can try |
|---|---|---|---|
| Administrator | `demo_admin` | `/adminlogin` | Approve sign-ups, manage doctors and patients, see every prescription |
| Doctor | `demo_doctor` | `/doctorlogin` | See appointments, write a prescription, reply to patients, post on the blog |
| Patient | `demo_patient` | `/patientlogin` | Book an appointment, message a doctor, download a prescription PDF |
| Accountant | `demo_accountant` | `/accountantlogin` | Add medicine, update stock, search records by date |

Running it yourself? Create these accounts with `python manage.py create_demo_users`.
Please don't put real medical information into the demo.

---

## What it does

**Patients**
- Book an appointment and follow its status (pending → approved)
- Chat privately with a doctor
- Download every prescription as a PDF
- Leave feedback for the center

**Doctors**
- See their own appointments and patients
- Write digital prescriptions. Medicine is taken out of stock automatically, and the form warns when stock runs low.
- Write health tips and first-aid articles for the public blog

**Accountants**
- Keep the medicine stock up to date
- Spot medicines that are running low
- Search stock records between two dates

**Administrators**
- Approve or reject new doctors, patients and accountants
- Manage appointments, people, prescriptions, feedback and blog posts from one dashboard

Each role only sees its own part of the site. A patient who opens a doctor page is sent back to their own dashboard,
and nobody can read someone else's chat or prescription.

---

## Run it on your computer

You need Python 3.12 or newer.

```bash
git clone https://github.com/prityd825/NSTU_E_medical_Center.git
cd NSTU_E_medical_Center
python -m venv .venv
.venv\Scripts\activate          # on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py create_demo_users
python manage.py runserver
```

Then open http://127.0.0.1:8000 and sign in with one of the demo accounts.

Run the tests with `python manage.py test hospital`.

---

## Deploying

The repo is ready for [Render](https://render.com). Click the **Deploy to Render** button above, or create a
*Blueprint* from this repo. `render.yaml` and `build.sh` take care of installing packages, collecting static files,
running migrations and creating the demo accounts.

Settings come from environment variables:

| Variable | What it is |
|---|---|
| `SECRET_KEY` | Any long random string (Render generates one for you) |
| `DEBUG` | `False` on a server |
| `ALLOWED_HOSTS` | Your domain, e.g. `nstu-emedical.onrender.com` (Render's own domain is added automatically) |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Optional Gmail address and *app password* for the contact form and password reset |

> On Render's free plan the disk is reset on every deploy, so new sign-ups and uploads made on the live site
> won't survive a redeploy. Fine for a demo; for real use, switch to a hosted database.

---

## Built with

Django · Bootstrap 5 · SQLite · xhtml2pdf (prescription PDFs) · WhiteNoise · Gunicorn

```text
E-medical/     project settings and URLs
hospital/      models, views, forms, access rules, tests
templates/     pages (one layout per role)
static/        stylesheet, images, profile pictures
```

---

Made with care for the NSTU community. Found a bug or have an idea? Open an issue.
