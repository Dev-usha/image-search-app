import streamlit as st
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.api_client import APIClient

def show_reminders_interface():
    """Main reminders interface"""
    st.markdown("### ⏰ Smart Reminders")
    st.markdown("Never forget important medications, appointments, and daily tasks.")
    
    # Tabs for different reminder functions
    tab1, tab2, tab3 = st.tabs(["➕ Add Reminder", "📋 Active Reminders", "✅ Completed"])
    
    with tab1:
        show_add_reminder()
    
    with tab2:
        show_active_reminders()
    
    with tab3:
        show_completed_reminders()

def show_add_reminder():
    """Interface for adding new reminders"""
    st.markdown("#### ➕ Add New Reminder")
    
    with st.form("add_reminder_form"):
        # Reminder text
        reminder_text = st.text_area(
            "What would you like to be reminded about?",
            placeholder="Take morning medication, Doctor appointment at 2 PM, Call Sarah...",
            height=100,
            help="Describe what you need to remember"
        )
        
        # Reminder type and time
        col1, col2 = st.columns(2)
        
        with col1:
            reminder_type = st.selectbox(
                "Reminder Type",
                options=[
                    "Medication",
                    "Appointment", 
                    "Daily Task",
                    "Exercise",
                    "Social",
                    "Health Check",
                    "General"
                ],
                help="Choose the type of reminder"
            )
        
        with col2:
            reminder_time = st.time_input(
                "Reminder Time",
                value=datetime.now().time(),
                help="When should you be reminded?"
            )
        
        # Additional options
        col1, col2 = st.columns(2)
        
        with col1:
            reminder_date = st.date_input(
                "Reminder Date",
                value=datetime.now().date(),
                min_value=datetime.now().date(),
                help="Which date for this reminder?"
            )
        
        with col2:
            repeat_option = st.selectbox(
                "Repeat",
                options=["Once", "Daily", "Weekly", "Monthly"],
                help="How often should this reminder repeat?"
            )
        
        # Priority level
        priority = st.selectbox(
            "Priority Level",
            options=["🔴 High", "🟡 Medium", "🟢 Low"],
            index=1,
            help="How important is this reminder?"
        )
        
        # Additional notes
        notes = st.text_input(
            "Additional Notes (Optional)",
            placeholder="Any extra details or instructions...",
            help="Add any additional context"
        )
        
        # Submit button
        submitted = st.form_submit_button("⏰ Set Reminder", type="primary", use_container_width=True)
        
        if submitted:
            if reminder_text.strip():
                save_reminder(reminder_text, reminder_type, reminder_date, reminder_time, repeat_option, priority, notes)
            else:
                st.error("Please enter what you'd like to be reminded about.")

def save_reminder(text, reminder_type, date, time, repeat, priority, notes):
    """Save a new reminder"""
    try:
        api_client = st.session_state.api_client
        
        # Combine date and time
        reminder_datetime = datetime.combine(date, time)
        
        # Prepare metadata
        metadata = {
            "reminder_type": reminder_type,
            "reminder_date": date.isoformat(),
            "reminder_time": time.isoformat(),
            "repeat_option": repeat,
            "priority": priority,
            "notes": notes,
            "user_name": st.session_state.user_name,
            "created_at": datetime.now().isoformat()
        }
        
        # Save reminder
        result = api_client.add_reminder(
            text=text,
            reminder_time=reminder_datetime.isoformat(),
            reminder_type=reminder_type.lower(),
            is_completed=False
        )
        
        if result.get("status") == "success":
            st.success("✅ Reminder set successfully!")
            st.balloons()
            
            # Show confirmation
            with st.expander("Reminder Details", expanded=True):
                st.markdown(f"**What:** {text}")
                st.markdown(f"**When:** {date.strftime('%B %d, %Y')} at {time.strftime('%I:%M %p')}")
                st.markdown(f"**Type:** {reminder_type}")
                st.markdown(f"**Priority:** {priority}")
                if repeat != "Once":
                    st.markdown(f"**Repeats:** {repeat}")
                if notes:
                    st.markdown(f"**Notes:** {notes}")
        else:
            st.error("Failed to set reminder. Please try again.")
            
    except Exception as e:
        st.error(f"Error saving reminder: {e}")

def show_active_reminders():
    """Show active (incomplete) reminders"""
    st.markdown("#### 📋 Active Reminders")
    
    try:
        api_client = st.session_state.api_client
        
        # Get active reminders
        reminders = api_client.get_reminders(completed=False)
        
        if reminders:
            st.markdown(f"You have {len(reminders)} active reminders")
            
            # Sort by priority and date
            sorted_reminders = sort_reminders_by_priority(reminders)
            
            for i, reminder in enumerate(sorted_reminders):
                show_reminder_card(reminder, i, is_active=True)
        else:
            st.info("No active reminders. Add a new reminder to get started!")
            
        # Quick add buttons
        st.markdown("#### 🚀 Quick Add")
        show_quick_reminder_buttons()
        
    except Exception as e:
        st.error(f"Error loading active reminders: {e}")

def show_completed_reminders():
    """Show completed reminders"""
    st.markdown("#### ✅ Completed Reminders")
    
    try:
        api_client = st.session_state.api_client
        
        # Get completed reminders
        reminders = api_client.get_reminders(completed=True)
        
        if reminders:
            st.markdown(f"You've completed {len(reminders)} reminders")
            
            # Show recent completed reminders
            recent_reminders = reminders[:20]  # Show last 20
            
            for i, reminder in enumerate(recent_reminders):
                show_reminder_card(reminder, i, is_active=False)
        else:
            st.info("No completed reminders yet. Complete some reminders to see them here!")
            
    except Exception as e:
        st.error(f"Error loading completed reminders: {e}")

def show_reminder_card(reminder, index, is_active=True):
    """Display a reminder card"""
    text = reminder.get('text', '')
    metadata = reminder.get('metadata', {})
    reminder_id = reminder.get('id', '')
    
    # Extract reminder details
    reminder_type = metadata.get('reminder_type', 'General')
    priority = metadata.get('priority', '🟡 Medium')
    notes = metadata.get('notes', '')
    reminder_time_str = metadata.get('reminder_time', '')
    
    # Format time
    try:
        if reminder_time_str:
            reminder_time = datetime.fromisoformat(reminder_time_str.replace('Z', '+00:00'))
            formatted_time = reminder_time.strftime("%B %d at %I:%M %p")
            
            # Check if overdue
            is_overdue = reminder_time < datetime.now() and is_active
        else:
            formatted_time = "No time set"
            is_overdue = False
    except:
        formatted_time = "Invalid time"
        is_overdue = False
    
    # Get emoji for reminder type
    type_emoji = get_reminder_type_emoji(reminder_type)
    
    # Create card with appropriate styling
    card_class = "reminder-overdue" if is_overdue else ("reminder-active" if is_active else "reminder-completed")
    
    with st.expander(f"{type_emoji} {text} - {formatted_time}", expanded=False):
        # Reminder details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Type:** {reminder_type}")
            st.markdown(f"**Priority:** {priority}")
            
        with col2:
            st.markdown(f"**Time:** {formatted_time}")
            if is_overdue:
                st.markdown("🚨 **Status:** Overdue")
            elif is_active:
                st.markdown("⏳ **Status:** Pending")
            else:
                st.markdown("✅ **Status:** Completed")
        
        if notes:
            st.markdown(f"**Notes:** {notes}")
        
        # Action buttons
        if is_active:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ Mark Complete", key=f"complete_{index}", use_container_width=True):
                    complete_reminder(reminder_id, text)
            
            with col2:
                if st.button("⏰ Snooze 1hr", key=f"snooze_{index}", use_container_width=True):
                    snooze_reminder(reminder_id, 60)
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{index}", use_container_width=True):
                    delete_reminder(reminder_id, text)

def complete_reminder(reminder_id, reminder_text):
    """Mark reminder as completed"""
    try:
        api_client = st.session_state.api_client
        
        result = api_client.update_reminder(reminder_id, is_completed=True)
        
        if result.get("status") == "success":
            st.success(f"✅ Marked '{reminder_text}' as completed!")
            st.rerun()
        else:
            st.error("Failed to update reminder.")
            
    except Exception as e:
        st.error(f"Error completing reminder: {e}")

def snooze_reminder(reminder_id, minutes):
    """Snooze reminder for specified minutes"""
    # This would require backend support for updating reminder times
    st.info(f"Snoozed for {minutes} minutes! (Feature coming soon)")

def delete_reminder(reminder_id, reminder_text):
    """Delete a reminder"""
    # This would require backend support for deleting reminders
    if st.checkbox(f"Confirm deletion of '{reminder_text}'", key=f"confirm_delete_{reminder_id}"):
        st.warning("Reminder deletion feature coming soon!")

def show_quick_reminder_buttons():
    """Show quick add reminder buttons"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💊 Take Medication", key="quick_med", use_container_width=True):
            add_quick_reminder("Take medication", "Medication", 8, 0)  # 8:00 AM
    
    with col2:
        if st.button("🚰 Drink Water", key="quick_water", use_container_width=True):
            add_quick_reminder("Drink a glass of water", "Health Check", None, None, repeat="Daily")
    
    with col3:
        if st.button("🏃 Exercise", key="quick_exercise", use_container_width=True):
            add_quick_reminder("Do daily exercise", "Exercise", 17, 0)  # 5:00 PM
    
    with col4:
        if st.button("📞 Call Family", key="quick_call", use_container_width=True):
            add_quick_reminder("Call family member", "Social", 14, 0)  # 2:00 PM

def add_quick_reminder(text, reminder_type, hour=None, minute=None, repeat="Once"):
    """Add a quick reminder with default settings"""
    try:
        # Use current time if not specified
        if hour is None or minute is None:
            reminder_time = datetime.now() + timedelta(hours=1)
        else:
            today = datetime.now().date()
            reminder_time = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
            
            # If time has passed today, set for tomorrow
            if reminder_time < datetime.now():
                reminder_time += timedelta(days=1)
        
        api_client = st.session_state.api_client
        
        result = api_client.add_reminder(
            text=text,
            reminder_time=reminder_time.isoformat(),
            reminder_type=reminder_type.lower(),
            is_completed=False
        )
        
        if result.get("status") == "success":
            st.success(f"✅ Quick reminder set: {text}")
            st.rerun()
        else:
            st.error("Failed to set quick reminder.")
            
    except Exception as e:
        st.error(f"Error setting quick reminder: {e}")

def sort_reminders_by_priority(reminders):
    """Sort reminders by priority and time"""
    priority_order = {"🔴 High": 0, "🟡 Medium": 1, "🟢 Low": 2}
    
    def sort_key(reminder):
        metadata = reminder.get('metadata', {})
        priority = metadata.get('priority', '🟡 Medium')
        priority_num = priority_order.get(priority, 1)
        
        # Get reminder time for secondary sort
        reminder_time_str = metadata.get('reminder_time', '')
        try:
            if reminder_time_str:
                reminder_time = datetime.fromisoformat(reminder_time_str.replace('Z', '+00:00'))
                return (priority_num, reminder_time)
        except:
            pass
        
        return (priority_num, datetime.now())
    
    return sorted(reminders, key=sort_key)

def get_reminder_type_emoji(reminder_type):
    """Get emoji for reminder type"""
    emojis = {
        "Medication": "💊",
        "Appointment": "🏥", 
        "Daily Task": "📋",
        "Exercise": "🏃",
        "Social": "👥",
        "Health Check": "🩺",
        "General": "⏰"
    }
    return emojis.get(reminder_type, "⏰")

def show_reminder_statistics():
    """Show reminder statistics"""
    try:
        api_client = st.session_state.api_client
        
        # Get all reminders
        all_reminders = api_client.get_reminders()
        active_reminders = api_client.get_reminders(completed=False)
        completed_reminders = api_client.get_reminders(completed=True)
        
        st.markdown("#### 📊 Reminder Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Reminders", len(all_reminders))
        
        with col2:
            st.metric("Active", len(active_reminders))
        
        with col3:
            st.metric("Completed", len(completed_reminders))
        
        with col4:
            if len(all_reminders) > 0:
                completion_rate = (len(completed_reminders) / len(all_reminders)) * 100
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        # Reminder type breakdown
        if all_reminders:
            st.markdown("##### Reminder Types")
            
            type_counts = {}
            for reminder in all_reminders:
                metadata = reminder.get('metadata', {})
                reminder_type = metadata.get('reminder_type', 'General')
                type_counts[reminder_type] = type_counts.get(reminder_type, 0) + 1
            
            for reminder_type, count in sorted(type_counts.items()):
                emoji = get_reminder_type_emoji(reminder_type)
                st.markdown(f"- {emoji} {reminder_type}: {count}")
        
    except Exception as e:
        st.error(f"Error loading reminder statistics: {e}")

def show_upcoming_reminders():
    """Show upcoming reminders for today and tomorrow"""
    st.markdown("#### 🔮 Upcoming Reminders")
    
    try:
        api_client = st.session_state.api_client
        
        # Get active reminders
        reminders = api_client.get_reminders(completed=False)
        
        if reminders:
            # Filter for today and tomorrow
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            today_reminders = []
            tomorrow_reminders = []
            
            for reminder in reminders:
                metadata = reminder.get('metadata', {})
                reminder_time_str = metadata.get('reminder_time', '')
                
                try:
                    if reminder_time_str:
                        reminder_time = datetime.fromisoformat(reminder_time_str.replace('Z', '+00:00'))
                        reminder_date = reminder_time.date()
                        
                        if reminder_date == today:
                            today_reminders.append(reminder)
                        elif reminder_date == tomorrow:
                            tomorrow_reminders.append(reminder)
                except:
                    continue
            
            # Show today's reminders
            if today_reminders:
                st.markdown("**📅 Today:**")
                for reminder in sorted(today_reminders, key=lambda x: x.get('metadata', {}).get('reminder_time', '')):
                    text = reminder.get('text', '')
                    metadata = reminder.get('metadata', {})
                    reminder_time_str = metadata.get('reminder_time', '')
                    
                    try:
                        reminder_time = datetime.fromisoformat(reminder_time_str.replace('Z', '+00:00'))
                        time_str = reminder_time.strftime("%I:%M %p")
                        
                        # Check if overdue
                        if reminder_time < datetime.now():
                            st.markdown(f"🚨 **{time_str}** - {text} (Overdue)")
                        else:
                            st.markdown(f"⏰ **{time_str}** - {text}")
                    except:
                        st.markdown(f"⏰ {text}")
            
            # Show tomorrow's reminders
            if tomorrow_reminders:
                st.markdown("**📅 Tomorrow:**")
                for reminder in sorted(tomorrow_reminders, key=lambda x: x.get('metadata', {}).get('reminder_time', '')):
                    text = reminder.get('text', '')
                    metadata = reminder.get('metadata', {})
                    reminder_time_str = metadata.get('reminder_time', '')
                    
                    try:
                        reminder_time = datetime.fromisoformat(reminder_time_str.replace('Z', '+00:00'))
                        time_str = reminder_time.strftime("%I:%M %p")
                        st.markdown(f"⏰ **{time_str}** - {text}")
                    except:
                        st.markdown(f"⏰ {text}")
            
            if not today_reminders and not tomorrow_reminders:
                st.info("No reminders for today or tomorrow.")
        
        else:
            st.info("No upcoming reminders.")
            
    except Exception as e:
        st.error(f"Error loading upcoming reminders: {e}")