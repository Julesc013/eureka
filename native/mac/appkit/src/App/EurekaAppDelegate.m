#import "EurekaAppDelegate.h"
#import "../UI/EurekaMainWindowController.h"

@interface EurekaAppDelegate ()
@property (nonatomic, strong) EurekaMainWindowController *mainWindowController;
@end

@implementation EurekaAppDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)notification
{
    (void)notification;
    self.mainWindowController = [[EurekaMainWindowController alloc] init];
    [self.mainWindowController showWindow:self];
}

- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender
{
    (void)sender;
    return YES;
}

@end
