import dayjs from "dayjs";


export function getThisWeekAndLastWeekDate() {
  const today = new Date();

  // Get current week's Monday
  const dayOfWeek = today.getDay(); // Sunday = 0, Monday = 1 ...
  const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // adjust if Sunday
  const thisWeekStart = new Date(today);
  thisWeekStart.setDate(today.getDate() + diffToMonday);
  thisWeekStart.setHours(0, 0, 0, 0);

  // Current week's Sunday
  const thisWeekEnd = new Date(thisWeekStart);
  thisWeekEnd.setDate(thisWeekStart.getDate() + 6);
  thisWeekEnd.setHours(23, 59, 59, 999);

  // Last week's Monday
  const lastWeekStart = new Date(thisWeekStart);
  lastWeekStart.setDate(thisWeekStart.getDate() - 7);

  // Last week's Sunday
  const lastWeekEnd = new Date(lastWeekStart);
  lastWeekEnd.setDate(lastWeekStart.getDate() + 6);

  return[ 
 {
 
      title:"Last Week",
      start: dayjs( dayjs(lastWeekStart).format("YYYY-MM-DD")),
      end:  dayjs( dayjs(lastWeekEnd).format("YYYY-MM-DD"))
    },
    {
   
      title:"This Week",
      start: dayjs(dayjs(thisWeekStart).format("YYYY-MM-DD")),
      end: dayjs(dayjs(thisWeekEnd).format("YYYY-MM-DD"))
    },
  ]
}
