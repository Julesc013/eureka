#import "EurekaMainWindowController.h"
#import "EurekaReadOnlySearchView.h"
#import "../Contract/EurekaSnapshotAdapter.h"
#import "../Contract/EurekaRelayAdapter.h"

@implementation EurekaMainWindowController

- (instancetype)init
{
    NSRect frame;
    NSWindow *window;
    EurekaReadOnlySearchView *searchView;
    NSString *summary;

    frame = NSMakeRect(100.0, 100.0, 760.0, 520.0);
    window = [[NSWindow alloc] initWithContentRect:frame
                                        styleMask:(NSTitledWindowMask | NSClosableWindowMask | NSResizableWindowMask)
                                          backing:NSBackingStoreBuffered
                                            defer:NO];
    self = [super initWithWindow:window];
    if (self) {
        summary = [NSString stringWithFormat:@"%@\n%@",
                   [EurekaSnapshotAdapter fixtureSummary],
                   [EurekaRelayAdapter fixtureSummary]];
        searchView = [[EurekaReadOnlySearchView alloc] initWithFrame:[[window contentView] bounds]];
        [searchView setAutoresizingMask:(NSViewWidthSizable | NSViewHeightSizable)];
        [searchView setSummaryText:summary];
        [[window contentView] addSubview:searchView];
        [window setTitle:@"Eureka AppKit Read-Only Skeleton"];
    }
    return self;
}

@end
