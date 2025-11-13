const DEFAULT_TEMPLATES = {
  101: {
    subject: 'Welcome to Our Service',
    content: (data: any) => `
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
    <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 6px; background-color: #f9f9f9;">
        <h2 style="color: #007BFF; border-bottom: 2px solid #eee; padding-bottom: 10px;">Welcome, ${data.username || 'Customer'}!</h2>
        
        <p>The full template service is temporarily unavailable, but we confirm your account creation.</p>
        
        <p>Your new account ID is: <strong>${data.userId || 'N/A'}</strong></p>
        
        <div style="margin: 25px 0;">
            <a href="${data.loginLink || '#'}" 
               style="background-color: #007BFF; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 4px; display: inline-block;">
                Access Your Account
            </a>
        </div>
        
        <p style="font-size: 12px; color: #888; margin-top: 30px;">Thank you for joining us.</p>
    </div>
</body>
</html>
`,
  },

  102: {
    subject: 'Confirmation: Notification Preferences Updated',
    content: (data: any) => `
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
    <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 6px; background-color: #f9f9f9;">
        <h2 style="color: #28a745; border-bottom: 2px solid #eee; padding-bottom: 10px;">Preferences Updated</h2>
        
        <p>Hi ${data.username || 'Customer'},</p>

        <p>This is a minimal confirmation because the main template service is offline.</p>
        
        <p>Your settings were successfully changed on: <strong>${data.updateDate || 'Today'}</strong></p>
        
        <p>If this was not you, please visit your settings immediately:</p>
        
        <div style="margin: 20px 0;">
            <a href="${data.settingsLink || '#'}" 
               style="color: #007BFF; text-decoration: underline;">
                Review Settings
            </a>
        </div>
        
        <p style="font-size: 12px; color: #888; margin-top: 30px;">This is an automated message.</p>
    </div>
</body>
</html>
`,
  },

  999: {
    subject: 'Critical System Alert',
    content: (data: any) =>
      `System failure detected for ID ${data.failureId || 'N/A'}. Please investigate. Full message payload: ${JSON.stringify(data)}`,
  },
};

export { DEFAULT_TEMPLATES };
