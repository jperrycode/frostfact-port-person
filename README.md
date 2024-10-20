Frost Factory Web Application
Overview

This web application for Frost Factory is built using Next.js for the front-end and Django REST Framework for the back-end API. It aims to provide a robust and user-friendly experience for managing events, bookings, and dynamic content related to Frost Factory’s operations. Below are the key features that make this project unique and efficient.
Key Features
1. Contact Form with Dynamic Routing

    Dynamic Routing: Depending on the selected inquiry subject, messages are routed to the appropriate email inbox.
    Email Functionality: Each message is sent to a designated mailbox for Frost Factory, and the user receives a confirmation email.
    Message Organization: All messages are saved in corresponding database tables with one-to-one relationships for efficient tracking and insights.

2. Dynamic Media Display

    Admin-Controlled Media: All media displayed on the site is dynamically managed through an admin dashboard, stored in an AWS container for fast load times.
    Real-Time Updates: The media and content sections can be updated on the fly, allowing Frost Factory to adjust visuals based on events, seasons, or current trends.

3. Events Calendar

    Public & Private Event Management: A dynamic calendar displays public events with detailed descriptions and private events with limited visibility.
    Interactive Event Details: Users can click on public events to learn more, with links to additional content or booking information.

4. Booking Form

    Simplified Booking Process: A calendar-linked booking form allows users to easily request rental dates and times, featuring preset choice fields for a smoother user experience.
    Internal & External Event Management: This feature helps in managing event bookings both internally for Frost Factory and externally for users.

Conclusion

These core features ensure that Frost Factory’s web application stands out by offering a seamless experience for managing content, events, and bookings. The dynamic capabilities of this system allow Frost Factory to adapt to changing needs and deliver an engaging, up-to-date platform.
