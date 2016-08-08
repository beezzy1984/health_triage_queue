
*health_triage_queue* - Patient Queue and Triage Module
------------------------------------------------------------

:Organization: Ministry of Health - Jamaica
:Authors: Marc Murray <murraym@moh.gov.jm>
:Copyright: 2015-2016 Ministry of Health (Jamaica)

This module includes the facility to create temporary patients for the
purpose of triage and to assign an ESI level to each triage entry.

It also includes a queue entry system to enqueue patients when they
arrive or when triage entries have been created.

Queue Entry
==============

The workflow is that patients will be called from the queue. The patient
at the top of the queue is quite likely next. The queue is sorted by
Priority, Last Call, Create Date. This means that queue entries created
earlier are higher up in the queue unless there are some with
higher priority

Each user should be looking at a filtered version of the queue based on
their role. For the most part, she should be able to filter the queue
by state to see who is next for her. She proceeds through her job by
just picking the first at the top of the queue, deciding whether to
call that client or leave it for another user, and if she decides to
call, she literally calls the client to the window/desk/office and click
the **call** button. This opens the *right window* for the user to deal
with the client/patient she has just called. 

When she has finished dealing with that person, she needs to click the
**dismiss** button before calling the next client/patient. That puts
the client/patient back in the queue, probably with a different state
but definitely at the end of the queue for ppl with that state.

Just below the details box at the top of the queue entry detail screen
is a text entry box. Any text entered there is saved in the queue entry
with the name of the user and the time it was written. This can be used
to pass notes between nurse and doctor, for example. Notes written here
are only in the queue entry though the facility exists to extract them
for other purposes.

Queue entries have 1 place for users to provide input and three buttons.

The three buttons, two of which are active at any one time are: *call*,
*dismiss* and *inspect*.

* **call**: Open the appropriate object related to the queue entry,
  set the queue entry to busy and update the last-call time.
* **dismiss**: Set the queue entry to not busy
* **inspect**: Open the related object without setting the busy flag

Interaction with other models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When an **Appointment** is changed from *Scheduled* to *Arrived/Waiting*
by clicking the *Patient Arrived* button, a queue entry is automatically
created and associated with that appointment.

When the Encounter related to this appointment is created through the
*Begin Encounter* button, this encounter is what gets opened when
**call** button is clicked.

Triage Entry
==============

The primary purpose of this model is to be able to enqueue people who
have not yet been verified as patients. In some cases they are already
in the system as patients or possibly as someone's next-of-kin.

A client presents at a facility for treatment and she has no prior
appointment. She is expected to join the queue of people waiting to be
triaged.

A triage entry is tied to either a patient or a named non-patient. It
contains fields for firstname, lastname, sex, age and a single ID
number. Until a patient is attached to the triage entry, these fields
remain active. The intention is that these fields will be used to
search for or create an appropriate patient record. 

When a Triage Entry is created, an associated queue entry is also
automatically created. This triage entry is opened when the **call**
button is clicked on the queue entry.

If the client is to be seen in this facility, today or later, we use
the **Set Appointment** button in the queue-entry to create one. This
is expected to be used by Medical Records staff setting the appointment.

But, it is the doctor that decides you are to be seen (i.e. given an
appointment) by selecting "To be seen" from the status drop-down.

If you are to be sent to a different facility, then a **referral**
is created.

(Patient) Referral
====================

