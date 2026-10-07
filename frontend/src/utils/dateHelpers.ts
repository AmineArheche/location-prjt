export const isExpiringSoon = (dateStr: string, daysThreshold = 7): boolean => {
  const target = new Date(dateStr);
  const now = new Date();
  const diff = (target.getTime() - now.getTime()) / (1000 * 3600 * 24);
  return diff >= 0 && diff <= daysThreshold;
};
