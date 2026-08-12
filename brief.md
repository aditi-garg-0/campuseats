## What CampusEats Does

CampusEats is basically a food ordering system designed for a college campus. It is meant for one institute where students have fixed lecture timings and there are only a limited number of food outlets available on campus. The main problem it tries to solve is something students commonly face during short breaks between lectures. Usually, a break may be only fifteen to twenty minutes, but if a student wants to get something to eat, they have to walk to the food outlet, stand in the queue, place the order, wait for the food to be prepared, and then walk back to class. If the queue is long, the student may end up missing the next lecture or simply skip eating.

CampusEats solves this problem by allowing students to order their food before they reach the outlet. A student can open the menu, select the required items, and place the order from anywhere on campus. The outlet receives the order immediately and can start preparing it while the student is still on the way. This means that the waiting time at the counter is reduced. The physical queue does not completely disappear, but instead of making the student spend their short break standing at the counter, most of the preparation happens in the kitchen before the student arrives.

The system is intentionally kept simple and focused on the campus environment. It does not include delivery riders, city-wide food delivery, or a large payment system connecting multiple businesses. The idea is simply to provide a small and practical food ordering system that solves the specific problem students face inside the institute.

## Who Uses It

There are three main types of users in CampusEats, and each one has a different role in the system.

The *student* is the main user of the application. A student can view the menus of different food outlets available on campus, select food items, place an order before reaching the outlet, and check the current status of the order. The student can also make the payment and, after completing the order, give a review or rating for the food or outlet.

The *outlet staff member* manages the orders for a particular food outlet. Their main job is to see new orders as they come in and update their status while preparing them. For example, an order can move from placed to preparing, then to ready, and finally to collected. Staff members can also update the availability of menu items. If something is currently unavailable or sold out, they can mark it as unavailable so that students cannot order it.

The *administrator* manages the overall CampusEats system. Unlike outlet staff, the administrator is not limited to one particular outlet. They can register new food outlets, manage staff accounts, decide which staff member belongs to which outlet, and view the overall activity of the platform. Basically, the administrator makes sure that the entire system is being managed properly.

## The Nouns

The nouns are basically the main things or objects that the CampusEats system needs to store information about. These will later become the main resources that our API will work with.

* *User* -- A person who has an account in the system. A user can have one of three roles: student, staff, or administrator.
* *Order* -- A food order placed by a student from a particular outlet. It contains the ordered items and has a status that changes as the order is prepared and collected.
* *Order Item* -- A particular item inside an order. It refers to a menu item and also stores the quantity ordered.
* *Payment* -- A record showing the payment made for a particular order.
* *Review* -- A rating and optional comment given by a student after completing an order.
* *Notification* -- A message sent to a student or staff member when there is an important change, especially when the status of an order changes.
* *Outlet* -- A food vendor operating on the campus. It has its own location, working hours, and menu.
* *Menu Item* -- A particular food or drink sold by an outlet. It contains information such as its name, price, and whether it is currently available.
  
## The Verbs

The verbs represent the actions that users can perform on these nouns. In the actual API, these actions will be represented using HTTP methods and appropriate status codes so that the system clearly communicates what happened.

* *Browse a menu* -- A student can view the food items available at an outlet along with their prices and availability.
* *Leave a review* -- A student who has completed an order can give a rating and optionally write a comment about their experience.
* *Register an outlet* -- An administrator can add a new food outlet to the CampusEats platform.
* *Receive a notification* -- Students or staff members can receive notifications when something important happens, such as an order status being changed.
* *Place an order* -- A student can select multiple items and submit an order to one particular outlet.
* *Track an order* -- A student can check the current status of an order and see whether it has been placed, is being prepared, is ready, or has been collected.
* *Update an order's status* -- Outlet staff can change the status of an order as it moves through the preparation process.
* *Mark a menu item as sold out or available* -- Outlet staff can change the availability of a food item so students can either order it or see that it is currently unavailable.
* *Pay for an order* -- The system records that the payment for a particular order has been completed.

When we put all these nouns and verbs together, we get the basic structure of CampusEats. The nouns tell us **what things exist in the system**, while the verbs tell us **what can be done with those things**. This gives us the basic contract for the application. Every API route that we create later should be connected to one of these resources and actions. In this way, we can keep the system focused and avoid adding unnecessary features that were never part of the original idea.
